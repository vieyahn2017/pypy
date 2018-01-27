```sql
CREATE TABLE file_upload_test(
  id SERIAL PRIMARY KEY,  
  filename varchar(100),
  location varchar(300),
  thumb varchar(300),
  contenttype varchar(100),
  size bigint,
  uptime timestamp(0) without time zone DEFAULT now(), 
  username varchar(100) default 'admin',
  tmp varchar(100));

ALTER TABLE file_upload_test OWNER TO lcic;

```