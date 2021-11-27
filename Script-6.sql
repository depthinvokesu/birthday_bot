/*

CREATE table user (
 user_id integer primary key,
 username varchar
 );
create table person (
  pers_name varchar,
  pers_bday varchar,
  user_id integer,
  foreign key (user_id) references user(user_id)
  ); 
create table add_cache (
 user_id integer,
 username varchar,
 pers_name varchar,
 pers_bday varchar
 );
create table delete_cache (
  user_id integer,
  pers_id integer,
  pers_num integer
  );
create table user_command (
  user_id integer,
  command_id integer,
  step_id integer
  );
 
*/

SELECT * from user;
SELECT * from person;
SELECT * from user_command;
SELECT * from add_cache;
SELECT * from delete_cache;

/*
update delete_cache set (pers_num, pers_id) = (3, 33) where (user_id, pers_id) = (4, 4)

delete from person where (user_id, pers_name) = (23, 'Person of Sep27')

SELECT * FROM person where (user_id, pers_name) = (17, 'Hugh Grant')

insert into delete_cache values (4,5,6)



SELECT * FROM person WHERE (STRFTIME('%m', 'now'), user_id) = (STRFTIME('%m', pers_bday), 12)

SELECT * FROM person WHERE (STRFTIME('%m', pers_bday), user_id) = ('10', 12)


select STRFTIME('%m', pers_bday) from person;
select STRFTIME('%m', 'now')


delete from add_cache 

select rowid, * from person

insert into delete_cache (user_id, pers_id, pers_num) values (1,1,1), (2,2,2)

update add_cache 
set pers_name = 'Buddha', pers_bday='1000-02-03'
where user_id = 18
*/