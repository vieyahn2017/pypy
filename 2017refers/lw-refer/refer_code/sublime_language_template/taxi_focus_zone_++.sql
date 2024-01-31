CREATE TABLE public.dt_taxifocusmessage
(
    id serial,
    vehicle_card character varying(32),
    "time" character varying(50),
    address character varying(32)
);
ALTER TABLE public.dt_taxifocusmessage
    OWNER to lcic;



CREATE TABLE public.dt_taxifocuszone
(
    id serial,
    address character varying(32),
    zone geometry,
    num integer
);

ALTER TABLE public.dt_taxifocuszone
    OWNER to lcic;


INSERT INTO public.dt_taxifocuszone
    (address, zone, num) 
VALUES 
(,,,);


SELECT ST_X(pt) AS lng, ST_Y(pt) AS lat, vehicle_card, time  FROM dt_vehiclegps 
WHERE 
ST_Contains('0106000020E610000001000000010300000001000000050000001955867137AD5A408CBD175FB48B3A40B2497EC4AFAE5A40580229B16B933A40B20FB22C98AE5A40761BD47E6B8B3A40C991CEC0C8AD5A404AED45B41D933A401955867137AD5A408CBD175FB48B3A40',
 pt)
AND time > '2017-2-15 11:01:01';


SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name , time
FROM dt_vehiclegps 
WHERE 
time > now() + interval '-40 d'  and
ST_Contains('0106000020E610000001000000010300000001000000050000001955867137AD5A408CBD175FB48B3A40B2497EC4AFAE5A40580229B16B933A40B20FB22C98AE5A40761BD47E6B8B3A40C991CEC0C8AD5A404AED45B41D933A401955867137AD5A408CBD175FB48B3A40',
 pt);



SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name , time
FROM dt_vehiclegps 
WHERE 
time > now() + interval '-40 d'  and
ST_Contains('0106000020E610000001000000010300000001000000050000001955867137AD5A408CBD175FB48B3A40B2497EC4AFAE5A40580229B16B933A40B20FB22C98AE5A40761BD47E6B8B3A40C991CEC0C8AD5A404AED45B41D933A401955867137AD5A408CBD175FB48B3A40',
 pt);



SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name , time
FROM dt_vehiclegps 
WHERE 
time > now() + interval '-40 d'  and
ST_Contains('0106000020E610000001000000010300000001000000050000001955867137AD5A408CBD175FB48B3A40410C74ED0BAE5A40950C0055DC903A4042D2A755F4AD5A40761BD47E6B8B3A40C991CEC0C8AD5A4088F71C588E903A401955867137AD5A408CBD175FB48B3A40', pt);





ST_Geomfromtext(
'MULTIPOLYGON(((26.5648 106.7109,26.5645 106.7117,26.5635 106.7109,26.5636 106.7098,26.5648 106.7109)))', 4326)


SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name 
FROM dt_vehiclegps 
WHERE 
ST_Contains('0106000020E610000001000000010300000001000000050000001955867137AD5A408CBD175FB48B3A40410C74ED0BAE5A40950C0055DC903A4042D2A755F4AD5A40761BD47E6B8B3A40C991CEC0C8AD5A4088F71C588E903A401955867137AD5A408CBD175FB48B3A40', pt);



SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name 
FROM dt_vehiclegps 
WHERE 
ST_Contains(ST_Makepolygon(
ST_Geomfromtext(
'LINESTRING(106 26,107 26,107 25,106 25,106 26)', 4326)
), pt);




SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name 
FROM dt_vehiclegps 
WHERE 
ST_Contains( 
ST_Geomfromtext(
'MULTIPOLYGON(((26.5648 106.7109,26.5645 106.7117,26.5635 106.7109,26.5636 106.7098,26.5648 106.7109)))', 4326)
 , pt);




SELECT 
ST_X(pt) AS lng, 
ST_Y(pt) AS lat, 
vehicle_card AS name 
FROM dt_vehiclegps 
WHERE 
ST_Contains( 
ST_Geomfromtext(
'MULTIPOLYGON(((106.707775 26.530117,106.709731 26.532038,106.711288 26.528664,106.708869 26.528048,106.707775 26.530117)))', 4326)
 , pt);





-- 随机写入50条测试数据
-- 为了测试方便，gps数据的时间为3小时以后，写入数据库时间是181分钟以后


DECLARE @cnt INT = 0;
DECLARE @ch INT = 10;
WHILE @cnt < 50
BEGIN
    SET @ch=cast( floor(rand()*10) as int)  
   INSERT INTO [TY20170330].[dbo].[VehicleData]
           ([VehId],[Time],[ReceiveTime] 
           ,[Longitude],[Latitude],[Velocity],[Angle]
           ,[Alarm],[Locate]) 
     VALUES
           ('JLC10012000'+ cast(@ch as varchar)
           ,DateAdd(hh,+3,GETDATE())
           ,DateAdd(mi,+181,GETDATE())
           ,26.65 + @ch*1.0/1000
           ,106.65 + @ch*1.0/1000
           ,40 + @ch/2
           ,45 + @ch
           ,0
           ,1)
   SET @cnt = @cnt + 1;
END;
