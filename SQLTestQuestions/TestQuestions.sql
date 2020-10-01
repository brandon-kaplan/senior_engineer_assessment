USE PersonDatabase;

/*********************
Hello! 
Please use the test data provided in the file 'PersonDatabase' to answer the following
questions. Please also import the dbo.Contacts flat file to a table for use. 
All answers should be executable on a MS SQL Server 2012 instance. 
***********************
QUESTION 1
The table dbo.Risk contains calculated risk scores for the population in dbo.Person. Write a 
query or group of queries that return the patient name, and their most recent risk level(s). 
Any patients that dont have a risk level should also be included in the results. 
**********************/

SELECT p.PersonName AS PatientName,
       rs.RiskLevel
FROM dbo.Person AS p
LEFT JOIN (
        SELECT r.PersonID,
               r.RiskLevel,
               r.RiskDateTime,
               DENSE_RANK() OVER (PARTITION BY r.PersonID ORDER BY r.RiskDateTime DESC) AS rn
        FROM dbo.Risk AS r
) AS rs ON rs.PersonID = p.PersonID AND rs.rn = 1;

/**********************
QUESTION 2
The table dbo.Person contains basic demographic information. The source system users 
input nicknames as strings inside parenthesis. Write a query or group of queries to 
return the full name and nickname of each person. The nickname should contain only letters 
or be blank if no nickname exists.
**********************/
IF OBJECT_ID(N'TempDB..#Names', N'U') IS NOT NULL
    DROP TABLE #Names;

SELECT p.PersonID,
	   CASE WHEN PATINDEX('%(%)%',p.PersonName) > 0 THEN SUBSTRING(p.PersonName,
															CHARINDEX('(', p.PersonName)+1,
															LEN(p.PersonName) - (CHARINDEX(')',REVERSE(p.PersonName)) -1) - CHARINDEX('(', p.PersonName) -1 
														) 
			ELSE ''
		END AS NickName,
		CASE WHEN PATINDEX('%(%)%',p.PersonName) > 0 THEN LEFT(p.PersonName,CHARINDEX('(', p.PersonName) -1) + LTRIM(RTRIM(SUBSTRING(p.PersonName,LEN(p.PersonName) - (CHARINDEX(')', REVERSE(p.PersonName)) -1) + 1, LEN(p.PersonName))))
			 ELSE P.PersonName
		END AS FullName
INTO #Names
FROM dbo.Person AS p

--The following is because source system appears to let in special characters. 
DECLARE @id INT, @nickname NVARCHAR(100)
WHILE ((SELECT COUNT(*) FROM #Names AS n WHERE n.NickName LIKE '%[^A-Za-z]%' ) > 0)
BEGIN
	SELECT TOP 1 @id = personId, @nickname = nickname FROM #names WHERE NickName LIKE '%[^A-Za-z]%' ORDER BY PersonID
	WHILE PATINDEX('%[^A-Za-z]%',@nickname) > 0 SET @nickname = STUFF(@nickname,PATINDEX('%[^A-Za-z]%',@nickname),1,'')
	UPDATE #Names SET NickName = @nickname WHERE PersonID = @id
END

SELECT n.FullName,
       n.NickName
FROM #Names AS n;

/*
Notes:
If all special characters were known, chaining replace('',')') would probably suffice and the while loop above would be unecessary.
Ideally this would be extracted into a function, or if possible edit the import script to split this out during transformation.
This will work on combinations such as "Mc'Leary", "()jim)", etc. User Input is always a tricky area to handle all scenarios.
*/

/**********************
QUESTION 6
Write a query to return risk data for all patients, all payers 
and a moving average of risk for that patient and payer in dbo.Risk. 
**********************/

SELECT r.PersonId,
       r.AttributedPayer,
       r.RiskScore,
       r.RiskLevel,
       r.RiskDateTime,
	   AVG(r.RiskScore) OVER (PARTITION BY r.PersonId, r.AttributedPayer ORDER BY r.RiskDateTime) AS RiskMovingAverage
FROM dbo.Risk AS r
ORDER BY r.PersonId, r.AttributedPayer, r.RiskDateTime;
