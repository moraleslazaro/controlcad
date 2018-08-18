BEGIN;

/* 
   Table needed to store files by DatabaseStorage API.
   Execute this script after run `manage.py syncdb`.
   Example:
      database> sqlite3 files.db < custom.sql
*/
CREATE TABLE "scan_files" (
    "filename" VARCHAR(256) NOT NULL PRIMARY KEY,
    "data" TEXT NOT NULL,
    "size" INTEGER NOT NULL
);

COMMIT;
