#include <cassert>  
#include <string>  
#include <iostream>
#include <chrono>

#include "leveldb/db.h"  

#define TEST_FREQUENCY  (10000)

char* randomstr()
{
    static char buf[1024];
    int len = rand() % 768 + 255;
    for (int i = 0; i < len; ++i) {
        buf[i] = 'A' + rand() % 26;
    }
    buf[len] = '\0';
    return buf;
}

int main() 
{
    leveldb::DB* db;
    leveldb::Options options;
    options.create_if_missing = true;

    // 打开数据库
    leveldb::Status status = leveldb::DB::Open(options, "./testdb", &db);
    assert(status.ok());

    srand(2017);
    std::string k[TEST_FREQUENCY];
    for (int i = 0; i < TEST_FREQUENCY; ++i) {
        k[i] = (randomstr());
    }
    std::string v("壹贰叁肆伍陆柒捌玖拾");
    v.append(v).append(v).append(v).append(v).append(v);

    // 测试添加
    {
        auto start = std::chrono::system_clock::now();
        for (int i = 0; i < TEST_FREQUENCY; ++i) {
            status = db->Put(leveldb::WriteOptions(), k[i], v);
            assert(status.ok());
        }
        auto end = std::chrono::system_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << TEST_FREQUENCY <<"次添加耗时: "
            << double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den
            << "秒" << std::endl;
    }
    // 测试获取
    {
        auto start = std::chrono::system_clock::now();
        std::string v2[TEST_FREQUENCY];
        for (int i = 0; i < TEST_FREQUENCY; ++i) {
            status = db->Get(leveldb::ReadOptions(), k[i], &v2[i]);
            assert(status.ok());
        }
        auto end = std::chrono::system_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << TEST_FREQUENCY <<"次获取耗时: "
            << double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den
            << "秒" << std::endl;
        // 验证获取结果是否正确
        std::string ss;
        for (int i = 0; i < TEST_FREQUENCY; ++i) {
            if (v2[i] != v) {
                std::cout << "第 " << i << " 个结果不正确" << std::endl;
                std::cout << v2[i] << std::endl;
            }
        }
    }
    // 测试修改
    {
        auto start = std::chrono::system_clock::now();
        v.append(v);
        for (int i = 0; i < TEST_FREQUENCY; ++i) {
            status = db->Put(leveldb::WriteOptions(), k[i], v);
            assert(status.ok());
        }
        auto end = std::chrono::system_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << TEST_FREQUENCY <<"次修改耗时: "
            << double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den
            << "秒" << std::endl;
    }

    // 测试删除
    {
        auto start = std::chrono::system_clock::now();
        for (int i = 0; i < TEST_FREQUENCY; ++i) {
            status = db->Delete(leveldb::WriteOptions(), k[i]);
            assert(status.ok());
        }
        auto end = std::chrono::system_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << TEST_FREQUENCY <<"次删除耗时: "
            << double(duration.count()) * std::chrono::microseconds::period::num / std::chrono::microseconds::period::den
            << "秒" << std::endl;
    }
    delete db;
    return 0;
}