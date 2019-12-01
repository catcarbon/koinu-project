use KoinuProject;
set charset utf8mb4;

-- xiaogou
insert into User values(
    NULL,
    'GuanDian',
    '$argon2id$v=19$m=102400,t=2,p=8$7cZ6npqGdD5AB/M0eiwlYg$HjNq32iTg59HOFPMeBT7fw',
    7,
    DEFAULT
);

-- woshisb111
insert into User values(
    NULL,
    'NanjoYoshino',
    '$argon2id$v=19$m=102400,t=2,p=8$9iF7kSMMNC1KNE5TiJR0cw$Ggcb27N+I1NxTmqvh2tkwA',
    7,
    DEFAULT
);

-- ohleegay
insert into User values(
    NULL,
    'RandomGuy',
    '$argon2id$v=19$m=102400,t=2,p=8$eShe4GKmMfX8qY0PtmHKHQ$MlB0Oj3GHhhWYCDeHdNeJg',
    4,
    DEFAULT
);

-- disabled
insert into User values(
    NULL,
    'DisabledAccount',
    '$argon2id$v=19$m=102400,t=2,p=8$XTSQE0hf8P/E0Qju1Bl+cA$o+RO0pfFhm/NmGqnQ1hBtg',
    4,
    0
);