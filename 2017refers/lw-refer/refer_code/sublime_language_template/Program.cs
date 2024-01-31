using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Configuration;
using System.Data.SqlClient;
using System.Net;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using UBPBaseLib.Logger;

namespace UploadTrajectorySample
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            string connectionString = "", connectionString2="", companyName="", trajectoryUrl = "", serviceUrl="";
            int num=1000, frequency=5;
            try {
                connectionString = ConfigurationManager.ConnectionStrings["GPSDBConnectString"].ConnectionString;
                connectionString2 = ConfigurationManager.ConnectionStrings["StaticDBConnectString"].ConnectionString;
                companyName = ConfigurationManager.AppSettings["CompanyName"];
                trajectoryUrl = ConfigurationManager.AppSettings["TrajectoryUrl"];
                serviceUrl = ConfigurationManager.AppSettings["ServiceUrl"];
                num = int.Parse(ConfigurationManager.AppSettings["PostMaxNumber"]);
                frequency = int.Parse(ConfigurationManager.AppSettings["Frequency"]);
            }
            catch (NullReferenceException x)
            {
                Console.WriteLine("正确书写配置文件，请核对相关字段的正确性:");
                Console.WriteLine("connectionStrings>[\"GPSDBConnectString\"]");
                Console.WriteLine("connectionStrings>[\"StaticDBConnectString\"]");
                Console.WriteLine("appSettings>[\"CompanyName\"]");
                Console.WriteLine("appSettings>[\"TrajectoryUrl\"]");
                Console.WriteLine("appSettings>[\"ServiceUrl\"]");
                Console.WriteLine("appSettings>[\"PostMaxNumber\"]");
                Console.WriteLine("appSettings>[\"Frequency\"]\n");
                return;
            }
            DateTime dateTime = DateTime.Now.AddSeconds(-frequency);

            IEventLogger eventLogger = new CompositeLogger(new IEventLogger[]
            {
                new FileSplitErrorLogger("logerror", ""),
                new ConsoleLogger(),
                new FileSplitLogger("log", "")
            });
            Dictionary<string, string> dictionary = Program.LoadCarIdToCarNo(connectionString2, eventLogger);
            if (dictionary == null)
            {
                Thread.Sleep(3000);
                return;
            }
            eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Information, new
            {
                carNumber = dictionary.Count
            }, "LoadCarIdToCarNo succeed");
            while (true)
            {
                // 1 LoadDataFromDB
                eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Information, new
                {
                }, "Get data since: " + dateTime);
                DateTime minValue = DateTime.MinValue;
                dateTime = ((Math.Abs((DateTime.Now - dateTime).TotalMinutes) >= 30.0) ? DateTime.Now.AddSeconds(-frequency) : dateTime);
                List<Trajectory> list = Program.LoadDataFromDB(connectionString + DateTime.Now.ToString("yyMM"), dateTime, dictionary, eventLogger, ref minValue);
                eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Information, new
                {
                    TrajectoryNumberCount = list.Count,
                    MaxTime = minValue
                }, "Get GPS data succeed");

                int i = 0;
                while (i < list.Count)
                {
                    List<Trajectory> list2 = new List<Trajectory>();
                    int num2 = i;
                    while (num2 < list.Count && list2.Count < num)
                    {
                        list2.Add(list[num2]);
                        num2++;
                    }
                    eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Information, new
                    {
                        TotalNumber = list.Count,
                        Left = list.Count - i,
                        PostNumber = list2.Count
                    }, "Post GPS Data");
                    try
                    {
                        List<Object> list_o = list2.ConvertAll(s => (object)s); // object作为PostData通用参数
                        Program.PostData(companyName, "trajectoryData", list_o, trajectoryUrl);
                        /* *  
                         * 不能直接这样 Program.PostData(companyName, "serviceData", list3, serviceUrl); 会报错
                         * 无法从“System.Collections.Generic.List < UploadTrajectorySample.Service >”转换为“System.Collections.Generic.List < object >”
                         * 
                         * */
                        i += list2.Count;
                    }
                    catch (Exception ex)
                    {
                        eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                        {
                            Exp = ex.ToString()
                        }, "PostData GPS Error");
                    }

                }

                /*
                //之前说增加运营数据，现在暂时又不需要了


                List<Service> list3 = Program.LoadData_Service(connectionString + DateTime.Now.ToString("yyMM"), dateTime, dictionary, eventLogger, ref minValue);
                eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Information, new
                {
                    ServiceNumberCount = list3.Count,
                    MaxTime = minValue
                }, "Get Service data succeed");
                try
                {
                    List<Object> list_o = list3.ConvertAll(s => (object)s); // object作为PostData通用参数
                    Program.PostData(companyName, "serviceData", list_o, serviceUrl);

                }
                catch (Exception ex)
                {
                    eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                    {
                        Exp = ex.ToString()
                    }, "PostData Service Error");
                }
                eventLogger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Information, new
                {
                    PostNumber = list3.Count
                }, "Post Service Data");

               */


                if (minValue != DateTime.MinValue)
                {
                    dateTime = minValue;
                }
                Thread.Sleep(1000 * frequency);
            }
        }

        private static Dictionary<string, string> LoadCarIdToCarNo(string connectString, IEventLogger logger)
        {
            Dictionary<string, string> dictionary = new Dictionary<string, string>();
            try
            {
                using (SqlConnection sqlConnection = new SqlConnection(connectString))
                {
                    SqlCommand sqlCommand = sqlConnection.CreateCommand();
                    sqlCommand.CommandText = "select id, veh_no_code from VehicleInfo";
                    sqlConnection.Open();
                    using (SqlDataReader sqlDataReader = sqlCommand.ExecuteReader())
                    {
                        while (sqlDataReader.Read())
                        {
                            if (!Convert.IsDBNull(sqlDataReader["id"]) && !Convert.IsDBNull("veh_no_code"))
                            {
                                dictionary[sqlDataReader["id"].ToString()] = sqlDataReader["veh_no_code"].ToString();
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                logger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                {
                    Exp = ex.ToString()
                }, "LoadCarIdToCarNo Error");
                return null;
            }
            return dictionary;
        }

        private static List<Service> LoadData_Service(string connectString, DateTime timeFrom, Dictionary<string, string> carIdToCarNo, IEventLogger logger, ref DateTime maxTime)
        {
            List<Service> list = new List<Service>();
            string text = "select vehicle_id, onaboard_time, getdown_time, money from service_datas where getdown_time>'" + timeFrom + "' ";
            try
            {
                using (SqlConnection sqlConnection = new SqlConnection(connectString))
                {
                    SqlCommand sqlCommand = sqlConnection.CreateCommand();
                    sqlCommand.CommandText = text;
                    sqlConnection.Open();
                    using (SqlDataReader sqlDataReader = sqlCommand.ExecuteReader())
                    {
                        while (sqlDataReader.Read())
                        {
                            string text2 = "";
                            try
                            {
                                text2 = sqlDataReader["vehicle_id"].ToString();
                                string taxiNo = carIdToCarNo[text2];
                                DateTime onaboard_time = DateTime.Parse(sqlDataReader["onaboard_time"].ToString());
                                DateTime getdown_time = DateTime.Parse(sqlDataReader["getdown_time"].ToString());
                                double money = double.Parse(sqlDataReader["money"].ToString());
                                maxTime = ((maxTime > getdown_time) ? maxTime : getdown_time);
                                list.Add(new Service
                                {
                                    taxiNo = taxiNo,
                                    boardingTime = onaboard_time,
                                    alightingTime = getdown_time,
                                    money = money
                                });
                            }
                            catch (Exception ex)
                            {
                                logger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                                {
                                    Exp = ex.ToString(),
                                    vechicleId = text2
                                }, "Parse Error");
                            }
                        }
                    }
                }
            }
            catch (Exception ex2)
            {
                logger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                {
                    Exp = ex2.ToString(),
                    Sql = text
                }, "Get Data From DB Error");
            }
            return list;
        }

        private static List<Trajectory> LoadDataFromDB(string connectString, DateTime timeFrom, Dictionary<string, string> carIdToCarNo, IEventLogger logger, ref DateTime maxTime)
        {
            List<Trajectory> list = new List<Trajectory>();
            string text = "select vehicle_id, local_time, pos_time, pos_latitude, pos_longitude, move_angle, move_speed, device_status_5, pos_invalidate, command_id, alarm_type from tb_gpsinfo where local_time>'" + timeFrom + "' order by pos_time";
            try
            {
                using (SqlConnection sqlConnection = new SqlConnection(connectString))
                {
                    SqlCommand sqlCommand = sqlConnection.CreateCommand();
                    sqlCommand.CommandText = text;
                    sqlConnection.Open();
                    using (SqlDataReader sqlDataReader = sqlCommand.ExecuteReader())
                    {
                        while (sqlDataReader.Read())
                        {
                            string text2 = "";
                            try
                            {
                                text2 = sqlDataReader["vehicle_id"].ToString();
                                string taxiNo = carIdToCarNo[text2];
                                DateTime time = DateTime.Parse(sqlDataReader["pos_time"].ToString());
                                double lat = double.Parse(sqlDataReader["pos_latitude"].ToString());
                                double lng = double.Parse(sqlDataReader["pos_longitude"].ToString());
                                double direction = double.Parse(sqlDataReader["move_angle"].ToString());
                                double speed = double.Parse(sqlDataReader["move_speed"].ToString()) / 3.6;
                                int num = int.Parse(sqlDataReader["device_status_5"].ToString());
                                int posInvalidate;
                                //Console.WriteLine(DBNull.Value.ToString());
                                object t_posInvalidate = sqlDataReader["pos_invalidate"];
                                if (t_posInvalidate == DBNull.Value)
                                {
                                    posInvalidate = 0;
                                }
                                else
                                {
                                    posInvalidate = int.Parse(t_posInvalidate.ToString());
                                }
                                int commandId; //208：注册信息;  209：报警;  210：故障;  212：定位;  214：附加事件
                                object t_commandId = sqlDataReader["command_id"];
                                if (t_commandId == DBNull.Value)
                                {
                                    commandId = 212;
                                }
                                else
                                {
                                    commandId = int.Parse(t_commandId.ToString());
                                }
                                int alarmType;
                                object t_alarmType = sqlDataReader["alarm_type"];
                                if (t_alarmType == DBNull.Value)
                                {
                                    alarmType = 0;
                                }
                                else
                                {
                                    alarmType = Program.getAlarmTypeByCommandIds(commandId, int.Parse(t_alarmType.ToString()));
                                }

                                string empty;
                                if (num % 2 == 1)
                                {
                                    empty = "no";
                                }
                                else
                                {
                                    empty = "yes";
                                }
                                DateTime dateTime = DateTime.Parse(sqlDataReader["local_time"].ToString());
                                maxTime = ((maxTime > dateTime) ? maxTime : dateTime);
                                list.Add(new Trajectory
                                {
                                    taxiNo = taxiNo,
                                    time = time,
                                    lat = lat,
                                    lng = lng,
                                    direction = direction,
                                    speed = speed,
                                    empty = empty,
                                    alarmType = alarmType,
                                    posInvalidate = posInvalidate
                                });
                            }
                            catch (Exception ex)
                            {
                                logger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                                {
                                    Exp = ex.ToString(),
                                    vechicleId = text2
                                }, "Parse Error");
                            }
                        }
                    }
                }
            }
            catch (Exception ex2)
            {
                logger.Log(LogEventId.UNASSIGNED_ID, LogLevel.Error, new
                {
                    Exp = ex2.ToString(),
                    Sql = text
                }, "Get Data From DB Error");
            }
            return list;
        }

        private static int getAlarmTypeByCommandIds(int commandId, int alarmType)
        {
            switch (commandId) //208：注册信息;  209：报警;  210：故障;  212：定位;  214：附加事件
            {
                case 208: return Program.findAlarmTypeInCommandId(alarmType, 
                    new Dictionary<int, int>
                    {
                        {16, 201}, /*GPRS连接注册*/
                        {17, 202}, /*GPRS上电注册*/
                        {18, 203}, /*GPRS定时注册*/
                    });
                case 214: return Program.findAlarmTypeInCommandId(alarmType,
                    new Dictionary<int, int>
                    {
                        {15, 501}, /*车辆点火*/
                        {16, 502}, /*车辆熄火*/
                        {19, 503}, /*上客*/
                        {20, 504}, /*下客*/
                        {30, 505}, /*出线路*/
                        {31, 506}, /*进线路*/
                    });
                case 210: return 301; //210：故障 接收那边给忽略了，我设置为301紧急报警
                case 209: return Program.findAlarmTypeInCommandId(alarmType,
                    new Dictionary<int, int>
                    {
                        {1, 301}, /*紧急报警*/
                        {2, 302}, /*非法启动*/
                        {3, 303}, /*被盗报警*/
                        {4, 304}, /*非法移动*/
                        {5, 305}, /*非法断线*/
                        {6, 306}, /*掉电报警*/
                        {8, 308}, /*超速报警*/
                        {9, 309}, /*看守报警*/
                        {10, 310}, /*碰撞/扩展报警*/
                        {11, 311}, /*GSM漫游报警*/
                        {12, 312}, /*偏航报警*/
                        {13, 313}, /*入界报警*/
                        {14, 314}, /*时段报警*/
                        {15, 315}, /*非法开锁报警*/
                        {16, 316}, /*超时报警*/
                        {17, 317}, /*GPS短路报警*/
                        {18, 318}, /*GPS开路报警*/
                        {19, 319}, /*低电报警*/
                        {20, 320}, /*趟间超时*/
                        {21, 321}, /*趟间停车超时*/
                        {22, 322}, /*非法卸货报警*/
                        {23, 323}, /*非法卸货*/
                        {24, 324}, /*停车不熄火报警*/
                        {25, 325}, /*开门报警*/
                        {26, 326}, /*偷油报警*/
                        {27, 327}, /*AD变化报警*/
                        {28, 328}, /*自动提示报警*/
                        {29, 329}, /*侧翻报警*/
                        {30, 330}, /*急刹报警*/
                        {31, 331}, /*超重报警*/
                        {4096, 4096}, /*电子封条开启*/
                        {4097, 4097}, /*电子封条关闭*/
                        {4098, 4098}, /*电子封条非法断线*/
                        {8192, 8192}, /*停车超时报警*/
                        {8193, 8193}, /*短信超流量报警*/
                        {8194, 8194}, /*GPRS超流量报警*/
                        {8195, 8195}, /*温度报警*/
                        {8196, 8196}, /*不打表报警*/
                        {8197, 8197}, /*拼客报警*/     
                     });
                case 212: return 0;
                default: return 0;
            }
        }

        private static int findAlarmTypeInCommandId(int k, Dictionary<int, int> dictionary)
        {
            try
            {
                return dictionary[k];
            }
            catch (KeyNotFoundException)
            {
                return 0;
            }
        }

        private static void PostData(string companyName, string dataName, List<Object> trajectoryData, string APIUrl)
        {
            JavaScriptSerializer javaScriptSerializer = new JavaScriptSerializer();
            javaScriptSerializer.MaxJsonLength = 2147483647;
            NameValueCollection nameValueCollection = new NameValueCollection();
            nameValueCollection["companyName"] = companyName;
            nameValueCollection[dataName] = javaScriptSerializer.Serialize(trajectoryData);
            using (WebClient webClient = new WebClient())
            {
                Encoding.UTF8.GetString(webClient.UploadValues(APIUrl, nameValueCollection));
            }
        }
        /*
        private static void PostData(string companyName, List<Trajectory> trajectoryData, string APIUrl)
        {
            JavaScriptSerializer javaScriptSerializer = new JavaScriptSerializer();
            javaScriptSerializer.MaxJsonLength = 2147483647;
            NameValueCollection nameValueCollection = new NameValueCollection();
            nameValueCollection["companyName"] = companyName;
            nameValueCollection["trajectoryData"] = javaScriptSerializer.Serialize(trajectoryData);
            using (WebClient webClient = new WebClient())
            {
                Encoding.UTF8.GetString(webClient.UploadValues(APIUrl, nameValueCollection));
            }
        }
        private static void PostData(string companyName, List<Service> serviceData, string APIUrl)
        {
            JavaScriptSerializer javaScriptSerializer = new JavaScriptSerializer();
            javaScriptSerializer.MaxJsonLength = 2147483647;
            NameValueCollection nameValueCollection = new NameValueCollection();
            nameValueCollection["companyName"] = companyName;
            nameValueCollection["serviceData"] = javaScriptSerializer.Serialize(serviceData);
            using (WebClient webClient = new WebClient())
            {
                Encoding.UTF8.GetString(webClient.UploadValues(APIUrl, nameValueCollection));
            }
        }
        */
    }
}
