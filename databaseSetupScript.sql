/*
					MySQL database script
	NOTE: please remember to change the passwords of the users before running this script.
	LINES: 7 & 8
*/
create database if not exists ue4renderstream;
create user if not exists 'stream_python_user'@'%' identified with mysql_native_password by '{$password:stream_python_user}';
create user if not exists 'stream_webserver_user'@'localhost' identified with mysql_native_password by '{$password:stream_webserver_user}';
grant select, update on ue4renderstream.* to 'stream_python_user'@'%';
grant select, insert on ue4renderstream.* to 'stream_webserver_user'@'localhost';
use ue4renderstream;
create table if not exists RenderStreamUploads(
	img_id int unsigned auto_increment primary key,
    imgName varchar(31) not null unique,
	rendered TINYINT DEFAULT 0 not null,
	uploadtime timestamp DEFAULT CURRENT_TIMESTAMP not null,
	rendertime timestamp DEFAULT '0000-00-00 00:00:00' not null
);