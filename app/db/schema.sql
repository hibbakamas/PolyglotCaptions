CREATE TABLE dbo.Captions (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    CreatedAt DATETIME2 NOT NULL,
    SessionId NVARCHAR(100) NULL,
    FromLang NVARCHAR(10) NOT NULL,
    ToLang NVARCHAR(10) NOT NULL,
    Transcript NVARCHAR(MAX) NOT NULL,
    TranslatedText NVARCHAR(MAX) NOT NULL,
    ProcessingMs INT NOT NULL
);


-- Helpful indexes for common queries
CREATE INDEX IX_Captions_CreatedAt ON dbo.Captions (CreatedAt DESC);
CREATE INDEX IX_Captions_SessionId ON dbo.Captions (SessionId);

