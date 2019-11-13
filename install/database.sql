create database if not exists koinu default charset utf8mb4
                                    default collate utf8mb4_unicode_ci;

use koinu;

-- foreign keys should restrict update/delete because all of them reference
--   some kind of auto_increment primary key
-- removing a row from frontend view is done by setting status to disabled
-- all foreign keys are indexed by default
-- passwords use argon2id hash
--   if using default argon2-cffi settings, hash length is 77

create table if not exists koinu_users (
    uid int not null primary key auto_increment,
    email varchar(64) default NULL,
    display_name varchar(32) default 'new_user',
    password_hash varchar(255) default NULL,
    user_created datetime default current_timestamp,
    last_active datetime default current_timestamp on update current_timestamp,
    user_status tinyint default 1
);

create unique index koinu_users_email on koinu_users(email);
create unique index koinu_users_display_name on koinu_users(display_name);
create index koinu_users_last_active on koinu_users(last_active);

create table if not exists koinu_channels (
    cid int not null primary key auto_increment,
    channel_name varchar(32) default 'new_channel',
    description text,
    channel_admin_uid int not null default 1,
    channel_created datetime default current_timestamp,
    channel_last_update datetime default current_timestamp on update current_timestamp,
    channel_status tinyint default 1,

    foreign key (channel_admin_uid) references koinu_users(uid)
                                    on delete restrict
                                    on update restrict
);

create index koinu_channels_channel_name on koinu_channels(channel_name);

create table if not exists koinu_articles (
    aid int not null primary key auto_increment,
    title varchar(64) default 'new_article',
    content text,
    article_channel_cid int not null,
    published datetime default current_timestamp,
    article_last_update datetime default current_timestamp on update current_timestamp,
    article_status tinyint default 1,

    foreign key (article_channel_cid) references koinu_channels(cid)
                                      on delete restrict
                                      on update restrict
);

create index koinu_articles_title on koinu_articles(title);
create index koinu_articles_last_update on koinu_articles(article_last_update);

create table if not exists koinu_comments (
    coid int not null primary key auto_increment,
    comment_body tinytext,
    comment_article_aid int not null,
    comment_user_uid int not null,
    comment_time datetime default current_timestamp,
    comment_status tinyint default 1,

    foreign key (comment_article_aid) references koinu_articles(aid)
                                      on delete restrict
                                      on update restrict,

    foreign key (comment_user_uid) references koinu_users(uid)
                                   on delete restrict
                                   on update restrict
);

insert into koinu_users values(
    NULL,
    'admin@koinu-project.com',
    'koinu-admin',
    NULL,
    NULL,
    NULL,
    0
)