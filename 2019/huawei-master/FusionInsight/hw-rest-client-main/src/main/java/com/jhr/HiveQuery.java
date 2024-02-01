package com.jhr;

import cn.hutool.core.io.IoUtil;
import cn.hutool.core.util.ArrayUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.alibaba.druid.DbType;
import com.alibaba.druid.sql.SQLUtils;
import com.alibaba.druid.sql.ast.SQLExpr;
import com.alibaba.druid.sql.ast.SQLLimit;
import com.alibaba.druid.sql.ast.SQLStatement;
import com.alibaba.druid.sql.ast.statement.*;
import okhttp3.FormBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.spark.sql.SparkSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.util.concurrent.TimeUnit;

/**
 * @author xukun
 * @since 1.0
 */
public class HiveQuery {
    private static final Logger LOGGER = LoggerFactory.getLogger(HiveQuery.class);

    private static final OkHttpClient HTTP_CLIENT;

    private static FileSystem fileSystem;

    private static SparkSession sparkSession;

    private static boolean isPage;

    private static int page = Integer.MAX_VALUE;

    static {
        // 设置超时时间
        HTTP_CLIENT = new OkHttpClient.Builder().retryOnConnectionFailure(false).connectTimeout(5, TimeUnit.MINUTES)
                .writeTimeout(5, TimeUnit.MINUTES).readTimeout(60, TimeUnit.MINUTES).build();
    }

    /**
     * pageSize = 10
     * select * from a limit 10 > select * from a limit 10 (pass)
     * select * from a limit 2,10 > select * from a limit 2,10 (pass)
     * select * from a > select * from a limit 10 > select * from a limit 10,10 > ... (pass)
     * select * from a limit 100 > select * from a limit 10 > select * from a limit 10,10 > ... > select * from a limit 90,10 (pass)
     * select * from a limit 2,100 > select * from a limit 2,10 > select * from a limit 12,10 > ... > select * from a limit 92,100 (pass)
     * <p>
     * show tables (pass)
     * desc default.tab2 (pass)
     * create table tab3(id string,name string) (pass)
     *
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        if (ArrayUtil.isEmpty(args)) {
            throw new IllegalArgumentException("启动程序失败，参数不能为空！");
        }
        if (args.length < 2) {
            throw new IllegalArgumentException("启动程序失败，参数个数不正确！");
        }
        String hdfsUri = args[0];
        String hdfsParamPath = args[1];
        if (StrUtil.isBlank(hdfsUri) || StrUtil.isBlank(hdfsParamPath)) {
            throw new IllegalArgumentException("启动程序失败，参数不能为空！");
        }
        LOGGER.info("参数文件地址:" + hdfsParamPath);
        try {
            // 初始化sparksession
            sparkSession = SparkSession.builder().appName("Hw-Hive-Executor").getOrCreate();
            // 初始化hdfs
            initHdfs(hdfsUri);
            // 校验参数是否合法,并解析
            JSONObject paramObj = validateAndParseParam(hdfsParamPath);
            String url = paramObj.getStr("url");
            String hdfsPath = paramObj.getStr("hdfsPath");
            String id = paramObj.getStr("id");
            String sql = paramObj.getStr("sql");
            int pageSize = paramObj.getInt("pageSize", 100000);
            // 若目录不存在，创建目录
            Path parent = new Path(hdfsPath).getParent();
            if (!fileSystem.exists(parent)) {
                fileSystem.mkdirs(parent);
            }
            SQLStatement sqlStatement = SQLUtils.parseSingleStatement(sql, DbType.hive);
            boolean isDql = (sqlStatement instanceof SQLSelectStatement || sqlStatement instanceof SQLShowStatement
                    || sqlStatement instanceof SQLDescribeStatement || sqlStatement instanceof SQLSetStatement);
            sql = getProcessedSql(pageSize, sqlStatement);
            int pageNum = 1;
            // 查询接口，并写入结果到hdfs上
            url += "datasource/hive";
            execution(url, hdfsPath, id, sql, pageSize, pageNum, isDql);
        } finally {
            // 释放资源
            release();
        }
    }

    private static String getProcessedSql(int pageSize, SQLStatement sqlStatement) {
        if (sqlStatement instanceof SQLSelectStatement) {
            SQLSelectQueryBlock queryBlock = ((SQLSelectStatement) sqlStatement).getSelect().getQueryBlock();
            SQLLimit limit = queryBlock.getLimit();
            if (limit != null) {
                // 若limit大于预设值
                long rowCount = Long.parseLong(limit.getRowCount().toString());
                if (rowCount > pageSize) {
                    limit.setRowCount(pageSize);
                    isPage = true;
                    page = Math.round((float) rowCount / pageSize) - 1;
                }
            } else {
                // 若没有增加limit参数
                limit = new SQLLimit(pageSize);
                queryBlock.setLimit(limit);
                isPage = true;
            }
        }
        return sqlStatement.toLowerCaseString();
    }

    private static void release() throws IOException {
        if (fileSystem != null) {
            // 关闭
            fileSystem.close();
        }
        if (sparkSession != null) {
            sparkSession.stop();
        }
    }

    private static void initHdfs(String defaultFs) throws Exception {
        Configuration configuration = new Configuration();
        configuration.set("fs.defaultFs", defaultFs);
        fileSystem = FileSystem.get(new URI(defaultFs), configuration, "root");
    }

    private static String getProcessedSql(int pageSize, SQLStatement sqlStatement, int pageNum) {
        if (sqlStatement instanceof SQLSelectStatement) {
            SQLSelectQueryBlock queryBlock = ((SQLSelectStatement) sqlStatement).getSelect().getQueryBlock();
            SQLLimit limit = queryBlock.getLimit();
            final SQLExpr limitOffset = limit.getOffset();
            if (limitOffset == null) {
                // 计算offset
                int offset = (pageNum - 1) * pageSize;
                limit.setOffset(offset);
            } else {
                int offset = Integer.parseInt(limitOffset.toString()) + pageSize;
                limit.setOffset(offset);
            }
        }
        return sqlStatement.toLowerCaseString();
    }

    private static void execution(String baseUrl, String hdfsPath, String id, String sql, int pageSize, int pageNum, boolean isDql) throws Exception {
        String url = baseUrl + (isDql ? "/queryForList" : "/executeSql");
        LOGGER.info("执行SQL：{}", sql);
        // 填入参数
        FormBody formBody = new FormBody.Builder().add("dsourceId", id).add("sql", sql).build();
        Request request = new Request.Builder().url(url).post(formBody).build();
        try (Response response = HTTP_CLIENT.newCall(request).execute()) {
            if (response.isSuccessful()) {
                assert response.body() != null;
                String resultStr = response.body().string();
                JSONObject resultObj = JSONUtil.parseObj(resultStr);
                // 获取是否请求成功
                Boolean success = resultObj.getBool("success");
                if (!success) {
                    throw new RuntimeException("执行SQL失败：" + resultStr);
                }
                JSONArray data = resultObj.getJSONArray("data");
                // 判断结果是否为空
                if (!JSONUtil.isNull(data) && !data.isEmpty()) {
                    // 写入的文件名
                    String savePath = hdfsPath + StrUtil.C_SLASH + pageNum + ".json";
                    try (FSDataOutputStream outputStream = fileSystem.create(new Path(savePath))) {
                        // 写入到hdfs中
                        IoUtil.writeUtf8(outputStream, true, data.toString());
                        LOGGER.info("保存结果成功！存储路径：{}", savePath);
                    }
                    if (isPage && page > 0 && data.size() == pageSize) {
                        pageNum++;
                        page--;
                        if (isDql) {
                            SQLStatement sqlStatement = SQLUtils.parseSingleStatement(sql, DbType.hive);
                            sql = getProcessedSql(pageSize, sqlStatement, pageNum);
                        }
                        // 查询下一页
                        execution(baseUrl, hdfsPath, id, sql, pageSize, pageNum, isDql);
                    }
                }
            } else {
                throw new RuntimeException("请求接口失败！" + response);
            }
        }
    }

    private static JSONObject validateAndParseParam(String hdfsParamPath) throws IOException {
        try (FSDataInputStream inputStream = fileSystem.open(new Path(hdfsParamPath))) {
            // 从文件中获取参数信息
            String paramStr = IoUtil.readUtf8(inputStream);
            LOGGER.info("启动参数:" + paramStr);
            if (!JSONUtil.isJson(paramStr)) {
                throw new IllegalArgumentException("启动程序失败，参数不正确！");
            }
            JSONObject paramObj = JSONUtil.parseObj(paramStr);
            String url = paramObj.getStr("url");
            String hdfsPath = paramObj.getStr("hdfsPath");
            String id = paramObj.getStr("id");
            String sql = paramObj.getStr("sql");
            if (StrUtil.isBlank(url) || StrUtil.isBlank(hdfsPath) || StrUtil.isBlank(id) || StrUtil.isBlank(sql)) {
                throw new IllegalArgumentException("启动程序失败，参数不正确！");
            }
            return paramObj;
        }
    }
}
