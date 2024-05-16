
CREATE TABLE Dim_Company
(
  company_id int          NOT NULL GENERATED ALWAYS AS IDENTITY,
  size       varchar(100),
  name       varchar(100),
  PRIMARY KEY (company_id)
);

COMMENT ON TABLE Dim_Company IS 'company dimension table';

COMMENT ON COLUMN Dim_Company.size IS 'number of employees';

CREATE TABLE Dim_Date
(
  date_id int  NOT NULL GENERATED ALWAYS AS IDENTITY,
  date    date DEFAULT CURRENT_DATE(),
  day     int ,
  month   int ,
  year    int ,
  quarter int  NOT NULL,
  PRIMARY KEY (date_id)
);

CREATE TABLE Dim_Job_Role
(
  job_role_id int          NOT NULL GENERATED ALWAYS AS IDENTITY,
  category    varchar      NOT NULL,
  name        varchar(100),
  PRIMARY KEY (job_role_id)
);

COMMENT ON TABLE Dim_Job_Role IS 'job role dimension table';

CREATE TABLE Dim_Position
(
  position_id     int          NOT NULL GENERATED ALWAYS AS IDENTITY,
  company_id      int          NOT NULL,
  city            varchar(100),
  detail_position varchar(100),
  PRIMARY KEY (position_id)
);

COMMENT ON TABLE Dim_Position IS 'sub dimension table';

CREATE TABLE Dim_Skill
(
  skill_id int          NOT NULL GENERATED ALWAYS AS IDENTITY,
  category varchar(100) NOT NULL,
  name     varchar(100),
  PRIMARY KEY (skill_id)
);

COMMENT ON TABLE Dim_Skill IS 'skill dimension table';

CREATE TABLE Dim_Skill_List
(
  skill_job_post_id bigint NOT NULL,
  job_post_id       bigint NOT NULL,
  skill_id          int    NOT NULL,
  core_skill        bool   DEFAULT TRUE,
  PRIMARY KEY (skill_job_post_id)
);

COMMENT ON TABLE Dim_Skill_List IS 'skill list dimension table';

CREATE TABLE Dim_Source
(
  source_id int          NOT NULL GENERATED ALWAYS AS IDENTITY,
  name      varchar(100),
  url       varchar(255),
  PRIMARY KEY (source_id)
);

COMMENT ON TABLE Dim_Source IS 'source dimension table';

CREATE TABLE Fact_Job_Post
(
  job_post_id           bigint      NOT NULL GENERATED ALWAYS AS IDENTITY,
  company_id            int         NOT NULL,
  start_recruit_date_id int         NOT NULL,
  end_recruit_date_id   int         NOT NULL,
  job_role_id           int         NOT NULL,
  source_id             int         NOT NULL,
  salary_max            bigint     ,
  salary_min            bigint     ,
  years_of_experience   int        ,
  job_level             varchar(10),
  job_type              varchar(10),
  PRIMARY KEY (job_post_id)
);

COMMENT ON TABLE Fact_Job_Post IS 'job post fact table';

ALTER TABLE Fact_Job_Post
  ADD CONSTRAINT FK_Dim_Company_TO_Fact_Job_Post
    FOREIGN KEY (company_id)
    REFERENCES Dim_Company (company_id);

ALTER TABLE Fact_Job_Post
  ADD CONSTRAINT FK_Dim_Date_TO_Fact_Job_Post
    FOREIGN KEY (start_recruit_date_id)
    REFERENCES Dim_Date (date_id);

ALTER TABLE Fact_Job_Post
  ADD CONSTRAINT FK_Dim_Job_Role_TO_Fact_Job_Post
    FOREIGN KEY (job_role_id)
    REFERENCES Dim_Job_Role (job_role_id);

ALTER TABLE Fact_Job_Post
  ADD CONSTRAINT FK_Dim_Source_TO_Fact_Job_Post
    FOREIGN KEY (source_id)
    REFERENCES Dim_Source (source_id);

ALTER TABLE Dim_Skill_List
  ADD CONSTRAINT FK_Fact_Job_Post_TO_Dim_Skill_List
    FOREIGN KEY (job_post_id)
    REFERENCES Fact_Job_Post (job_post_id);

ALTER TABLE Dim_Skill_List
  ADD CONSTRAINT FK_Dim_Skill_TO_Dim_Skill_List
    FOREIGN KEY (skill_id)
    REFERENCES Dim_Skill (skill_id);

ALTER TABLE Fact_Job_Post
  ADD CONSTRAINT FK_Dim_Date_TO_Fact_Job_Post1
    FOREIGN KEY (end_recruit_date_id)
    REFERENCES Dim_Date (date_id);

ALTER TABLE Dim_Position
  ADD CONSTRAINT FK_Dim_Company_TO_Dim_Position
    FOREIGN KEY (company_id)
    REFERENCES Dim_Company (company_id);
