drop table if exists sessions;
create table sessions (
  id integer primary key autoincrement,
  title text not null,
  description text not null,
  convener text not null,
  space_id integer not null,
  FOREIGN KEY(space_id) REFERENCES spaces(id)
);

drop table if exists spaces;
create table spaces (
  id integer primary key autoincrement,
  space_name text not null,
  location_id integer not null,
  event_date date not null,
  start_time datetime not null,
  end_time datetime not null,
  FOREIGN KEY(location_id) REFERENCES locations(id)
);

drop table if exists locations;
create table locations (
  id integer primary key autoincrement,
  name text not null
)