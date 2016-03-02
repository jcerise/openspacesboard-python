drop table if exists sessions;
create table sessions (
  id integer primary key autoincrement,
  title text not null,
  description text not null,
  convener text not null
);

drop table if exists spaces;
create table spaces (
  id integer primary key autoincrement,
  name text not null,
  location text not null
);