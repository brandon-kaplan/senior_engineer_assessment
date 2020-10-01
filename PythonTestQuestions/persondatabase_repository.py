createTablesForImport = """
IF NOT EXISTS
(
    SELECT *
    FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[Demographics]')
          AND type IN ( N'U' )
)
BEGIN
    CREATE TABLE dbo.Demographics
    (
        Id INT NOT NULL,
        FirstName NVARCHAR(500) NULL,
        MiddleInitial NVARCHAR(10) NULL,
        LastName NVARCHAR(500) NULL,
        DOB DATETIME2(7) NULL,
        Sex NCHAR(1) NULL,
        FavoriteColor NVARCHAR(30) NULL,
        ProviderGroup NVARCHAR(100) NOT NULL,
        FileDate DATE NOT NULL,
        ImportDateTime DATETIME NOT NULL
            DEFAULT (GETDATE())
    );

END;
IF NOT EXISTS
(
    SELECT *
    FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[RiskQuarters]')
          AND type IN ( N'U' )
)
CREATE TABLE dbo.RiskQuarters
(
        ID INT NOT NULL,
        [Quarter] NVARCHAR(2) NOT NULL,
        AttributedFlag NVARCHAR(3) NOT NULL,
        RiskScore DECIMAL(18,17) NOT NULL,
        FileDate DATE NOT NULL,
        ImportDateTime DATETIME NOT NULL
)

"""

insert_demographics = """
INSERT INTO dbo.Demographics (
Id,
FirstName,
MiddleInitial,
LastName,
DOB,
Sex,
FavoriteColor,
ProviderGroup,
FileDate,
ImportDateTime
) VALUES (
    '{0}',    --ID
    '{1}',     --FirstName
    '{2}',     --MiddleInitial
    '{3}',     --LastName
    '{4}',     --DOB
    '{5}',     --Sex
    '{6}',     --FavoriteColor
    '{7}',     --ProviderGroup
    '{8}',     --FileDate
    GETDATE()
);
"""

insert_riskquarters= """
INSERT INTO dbo.RiskQuarters
(
    ID,
    Quarter,
    AttributedFlag,
    RiskScore,
    FileDate,
    ImportDateTime
)
VALUES
(   
    '{0}',      --ID
    '{1}',      --Quarter
    '{2}',      --AttributedFlag
    '{3}',      -- RiskScore - decimal(18, 17)
    '{4}',      -- FileDate - date
    GETDATE()   -- ImportDateTime - datetime
);
"""