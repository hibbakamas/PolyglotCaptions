----- Captions table -----
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Captions' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Captions (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Transcript NVARCHAR(MAX) NOT NULL,
        TranslatedText NVARCHAR(MAX) NOT NULL,
        FromLang NVARCHAR(10) NOT NULL,
        ToLang NVARCHAR(10) NOT NULL,
        ProcessingMs INT NOT NULL,
        SessionId NVARCHAR(50) NULL,
        UserId NVARCHAR(255) NOT NULL,   
        CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );

    CREATE INDEX IX_Captions_CreatedAt ON dbo.Captions (CreatedAt DESC);
    CREATE INDEX IX_Captions_SessionId ON dbo.Captions (SessionId);
    CREATE INDEX IX_Captions_UserId ON dbo.Captions (UserId); 
END


------ Users table ----- 
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Users (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Username NVARCHAR(100) NOT NULL UNIQUE,
        HashedPassword NVARCHAR(255) NOT NULL,
        CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );

    CREATE INDEX IX_Users_Username ON dbo.Users (Username);
END
