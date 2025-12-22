# **Easy Level:**
1. Show all the countries where customers live. 
```sql
SELECT DISTINCT "Country" FROM "Customer";
```
2. Show all the countries where customers live. 
```sql
SELECT "Title" FROM "Album";
```
3. Find the first and last names of all employees who are Sales Support Agents. 
```sql
SELECT "FirstName", "LastName" FROM "Employee" WHERE "Title" = 'Sales Support Agent';
```
4. What are the names of all the musical genres?  
```sql
SELECT "Name" FROM "Genre";
```
5. How many total tracks are there in the database?  
```sql
SELECT COUNT(*) FROM "Track";
```
6. Show the customers who live in Brazil. 
```sql
SELECT * FROM "Customer" WHERE "Country" = 'Brazil';
```
7. Find the name of the artist with the Artist ID of 50.  
```sql
SELECT "Name" FROM "Artist" WHERE "ArtistId" = 50;
```
8. List all invoices where the total amount is greater than 10 dollars. 
```sql
SELECT * FROM "Invoice" WHERE "Total" > 10;
```
9. Show the list of tracks ordered by their length in milliseconds from longest to shortest.  
```sql
SELECT "Name", "Milliseconds" FROM "Track" ORDER BY "Milliseconds" DESC;
```
10. What is the total number of distinct customers in the Invoice table? 
```sql
SELECT COUNT(DISTINCT "CustomerId") FROM "Invoice";
```
# **Medium Level:**
1. Show the list of all album titles along with the name of the artist who created them.  
```sql
SELECT T1."Title", T2."Name"
FROM "Album" AS T1
JOIN "Artist" AS T2 ON T1."ArtistId" = T2."ArtistId";
```
2.Find the first and last names of all customers and the first and last name of their assigned support agent. 
```sql
SELECT T1."FirstName", T1."LastName", T2."FirstName" AS "AgentFirstName", T2."LastName" AS "AgentLastName"
FROM "Customer" AS T1
JOIN "Employee" AS T2 ON T1."SupportRepId" = T2."EmployeeId";
```
3. List the names of all tracks that belong to the 'Rock' genre.  
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "Genre" AS T2 ON T1."GenreId" = T2."GenreId"
WHERE T2."Name" = 'Rock';
```
4. Show the total amount of money spent by the customer named 'Mark Taylor'.  
```sql
SELECT SUM(T1."Total")
FROM "Invoice" AS T1
JOIN "Customer" AS T2 ON T1."CustomerId" = T2."CustomerId"
WHERE T2."FirstName" = 'Mark' AND T2."LastName" = 'Taylor';
```
5. How many albums does the artist 'Led Zeppelin' have in the database?   
```sql
SELECT COUNT(*)
FROM "Album" AS T1
JOIN "Artist" AS T2 ON T1."ArtistId" = T2."ArtistId"
WHERE T2."Name" = 'Led Zeppelin';
```
6. List all the track names and the name of the media type for each track.   
```sql
SELECT T1."Name", T2."Name" AS "MediaType"
FROM "Track" AS T1
JOIN "MediaType" AS T2 ON T1."MediaTypeId" = T2."MediaTypeId";
```
7. Show the total number of tracks available for each genre name.  
```sql
SELECT T2."Name", COUNT(T1."TrackId")
FROM "Track" AS T1
JOIN "Genre" AS T2 ON T1."GenreId" = T2."GenreId"
GROUP BY T2."Name";

```
8. List the details of all invoices (Invoice ID and Date) for customers living in 'France'.   
```sql
SELECT T1."InvoiceId", T1."InvoiceDate"
FROM "Invoice" AS T1
JOIN "Customer" AS T2 ON T1."CustomerId" = T2."CustomerId"
WHERE T2."Country" = 'France';
```
9. Find the names of all tracks in the playlist named 'Classical'. 
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "PlaylistTrack" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Playlist" AS T3 ON T2."PlaylistId" = T3."PlaylistId"
WHERE T3."Name" = 'Classical';
```
10.  Who are the top 5 artists with the most albums? 
```sql
SELECT T2."Name", COUNT(T1."AlbumId")
FROM "Album" AS T1
JOIN "Artist" AS T2 ON T1."ArtistId" = T2."ArtistId"
GROUP BY T2."Name"
ORDER BY COUNT(T1."AlbumId") DESC
LIMIT 5;
```
11. List the names of all tracks included in the album 'Let There Be Rock'. 
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "Album" AS T2 ON T1."AlbumId" = T2."AlbumId"
WHERE T2."Title" = 'Let There Be Rock';
```
12. Find the full names of customers supported by the agent 'Margaret Park'. 
```sql
SELECT T1."FirstName", T1."LastName"
FROM "Customer" AS T1
JOIN "Employee" AS T2 ON T1."SupportRepId" = T2."EmployeeId"
WHERE T2."FirstName" = 'Margaret' AND T2."LastName" = 'Park';
```
13. Calculate the total quantity of items sold in Invoice ID 1.
```sql
SELECT SUM("Quantity")
FROM "InvoiceLine"
WHERE "InvoiceId" = 1;
```
14. Show the names of all tracks in the playlist 'Heavy Metal Classic'. 
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "PlaylistTrack" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Playlist" AS T3 ON T2."PlaylistId" = T3."PlaylistId"
WHERE T3."Name" = 'Heavy Metal Classic';
```
15. Find the total amount spent by the customer 'Leonie Köhler'. 
```sql
SELECT SUM(T1."Total")
FROM "Invoice" AS T1
JOIN "Customer" AS T2 ON T1."CustomerId" = T2."CustomerId"
WHERE T2."FirstName" = 'Leonie' AND T2."LastName" = 'Köhler';
```
16. How many tracks belong to the 'Latin' genre? 
```sql
SELECT COUNT(T1."TrackId")
FROM "Track" AS T1
JOIN "Genre" AS T2 ON T1."GenreId" = T2."GenreId"
WHERE T2."Name" = 'Latin';
```
17. What is the average duration (in milliseconds) of tracks in the 'Jazz' genre? 
```sql
SELECT AVG(T1."Milliseconds")
FROM "Track" AS T1
JOIN "Genre" AS T2 ON T1."GenreId" = T2."GenreId"
WHERE T2."Name" = 'Jazz';
```
18. List the tracks composed by 'Miles Davis' that are also in the 'Jazz' genre.  
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "Genre" AS T2 ON T1."GenreId" = T2."GenreId"
WHERE T1."Composer" = 'Miles Davis' AND T2."Name" = 'Jazz';
```
19. Show the first and last names of employees who report to 'Andrew Adams'.  
```sql
SELECT T1."FirstName", T1."LastName"
FROM "Employee" AS T1
JOIN "Employee" AS T2 ON T1."ReportsTo" = T2."EmployeeId"
WHERE T2."FirstName" = 'Andrew' AND T2."LastName" = 'Adams';
```
20. List the 5 shortest tracks in the database.  
```sql
SELECT "Name", "Milliseconds"
FROM "Track"
ORDER BY "Milliseconds" ASC
LIMIT 5;
```
21. Find the total revenue generated from invoices billed to the city 'Paris'. 
```sql
SELECT SUM("Total")
FROM "Invoice"
WHERE "BillingCity" = 'Paris';
```
22. List all artist names along with the number of albums they have released. 
```sql
SELECT T2."Name", COUNT(T1."AlbumId")
FROM "Album" AS T1
JOIN "Artist" AS T2 ON T1."ArtistId" = T2."ArtistId"
GROUP BY T2."Name";
```
23. Find the names of all tracks with the media type 'Purchased AAC audio file'.  
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "MediaType" AS T2 ON T1."MediaTypeId" = T2."MediaTypeId"
WHERE T2."Name" = 'Purchased AAC audio file';
```
24. List the Invoice ID and Total for all invoices where the customer lives in 'Canada'.  
```sql
SELECT T1."InvoiceId", T1."Total"
FROM "Invoice" AS T1
JOIN "Customer" AS T2 ON T1."CustomerId" = T2."CustomerId"
WHERE T2."Country" = 'Canada';
```
25. Count the total number of invoices issued to customers in the 'USA'. 
```sql
SELECT COUNT(T1."InvoiceId")
FROM "Invoice" AS T1
JOIN "Customer" AS T2 ON T1."CustomerId" = T2."CustomerId"
WHERE T2."Country" = 'USA';
```
26. List the distinct genre names present in the playlist named '90’s Music'. 
```sql
SELECT DISTINCT T3."Name"
FROM "PlaylistTrack" AS T1
JOIN "Track" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Genre" AS T3 ON T2."GenreId" = T3."GenreId"
JOIN "Playlist" AS T4 ON T1."PlaylistId" = T4."PlaylistId"
WHERE T4."Name" = '90’s Music';
```
27. Calculate the total price (sum of UnitPrice) of all tracks in the album 'Greatest Hits'.  
```sql
SELECT SUM(T1."UnitPrice")
FROM "Track" AS T1
JOIN "Album" AS T2 ON T1."AlbumId" = T2."AlbumId"
WHERE T2."Title" = 'Greatest Hits';
```
28. List the full names of employees hired in the year 2002. 
```sql
SELECT "FirstName", "LastName"
FROM "Employee"
WHERE "HireDate" BETWEEN '2002-01-01' AND '2002-12-31';
```
29. Find the name of the artist who performed the track 'Put The Finger On You'. 
```sql
SELECT T2."Name"
FROM "Track" AS T1
JOIN "Album" AS T3 ON T1."AlbumId" = T3."AlbumId"
JOIN "Artist" AS T2 ON T3."ArtistId" = T2."ArtistId"
WHERE T1."Name" = 'Put The Finger On You';
```
30. Show the total sum of invoice totals where the billing country is 'India'.
```sql
SELECT SUM("Total")
FROM "Invoice"
WHERE "BillingCountry" = 'India';
```
# **Hard Level:**
1. Find the names of all customers who have purchased a track from the 'Rock' genre. 
```sql
SELECT DISTINCT T1."FirstName", T1."LastName"
FROM "Customer" AS T1
JOIN "Invoice" AS T2 ON T1."CustomerId" = T2."CustomerId"
JOIN "InvoiceLine" AS T3 ON T2."InvoiceId" = T3."InvoiceId"
JOIN "Track" AS T4 ON T3."TrackId" = T4."TrackId"
JOIN "Genre" AS T5 ON T4."GenreId" = T5."GenreId"
WHERE T5."Name" = 'Rock';
```
2. Which artist has earned the most money from sales? 
```sql
SELECT T3."Name", SUM(T2."UnitPrice" * T2."Quantity") AS "TotalSales"
FROM "Track" AS T1
JOIN "InvoiceLine" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Album" AS T4 ON T1."AlbumId" = T4."AlbumId"
JOIN "Artist" AS T3 ON T4."ArtistId" = T3."ArtistId"
GROUP BY T3."Name"
ORDER BY "TotalSales" DESC
LIMIT 1;
```
3. List the titles of all albums that have tracks sold in the USA. 
```sql
SELECT DISTINCT T3."Title"
FROM "Invoice" AS T1
JOIN "InvoiceLine" AS T2 ON T1."InvoiceId" = T2."InvoiceId"
JOIN "Track" AS T4 ON T2."TrackId" = T4."TrackId"
JOIN "Album" AS T3 ON T4."AlbumId" = T3."AlbumId"
WHERE T1."BillingCountry" = 'USA';
```
4. Find the first and last name of the employee who supports the customer with the highest total payments. 
```sql
SELECT T1."FirstName", T1."LastName"
FROM "Employee" AS T1
JOIN "Customer" AS T2 ON T1."EmployeeId" = T2."SupportRepId"
ORDER BY (SELECT SUM("Total") FROM "Invoice" WHERE "CustomerId" = T2."CustomerId") DESC
LIMIT 1;
```
5. Which countries have more than 5 customers? 
```sql
SELECT "Country", COUNT("CustomerId")
FROM "Customer"
GROUP BY "Country"
HAVING COUNT("CustomerId") > 5;
```
6. List all tracks that are longer than the average track duration of the entire database. 
```sql
SELECT "Name", "Milliseconds"
FROM "Track"
WHERE "Milliseconds" > (SELECT AVG("Milliseconds") FROM "Track");
```
7. Find the names of artists who have never sold a track. 
```sql
SELECT T1."Name"
FROM "Artist" AS T1
LEFT JOIN "Album" AS T2 ON T1."ArtistId" = T2."ArtistId"
LEFT JOIN "Track" AS T3 ON T2."AlbumId" = T3."AlbumId"
LEFT JOIN "InvoiceLine" AS T4 ON T3."TrackId" = T4."TrackId"
WHERE T4."InvoiceLineId" IS NULL;

```
8. Show the top 3 most popular genres based on the number of tracks sold. 
```sql
SELECT T3."Name", COUNT(T2."InvoiceLineId")
FROM "Track" AS T1
JOIN "InvoiceLine" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Genre" AS T3 ON T1."GenreId" = T3."GenreId"
GROUP BY T3."Name"
ORDER BY COUNT(T2."InvoiceLineId") DESC
LIMIT 3;
```
9. List the names of all employees who are older than their manager. 
```sql
SELECT T1."FirstName", T1."LastName"
FROM "Employee" AS T1
JOIN "Employee" AS T2 ON T1."ReportsTo" = T2."EmployeeId"
WHERE T1."BirthDate" < T2."BirthDate";
```
10. Find the customer who has spent the most on music by the artist 'Iron Maiden'. 
```sql
SELECT T1."FirstName", T1."LastName", SUM(T3."UnitPrice" * T3."Quantity") AS "Spent"
FROM "Customer" AS T1
JOIN "Invoice" AS T2 ON T1."CustomerId" = T2."CustomerId"
JOIN "InvoiceLine" AS T3 ON T2."InvoiceId" = T3."InvoiceId"
JOIN "Track" AS T4 ON T3."TrackId" = T4."TrackId"
JOIN "Album" AS T5 ON T4."AlbumId" = T5."AlbumId"
JOIN "Artist" AS T6 ON T5."ArtistId" = T6."ArtistId"
WHERE T6."Name" = 'Iron Maiden'
GROUP BY T1."CustomerId", T1."FirstName", T1."LastName"
ORDER BY "Spent" DESC
LIMIT 1;
```
11. Calculate the average invoice total for each country, but only show countries where the average is greater than $5.50. 
```sql
SELECT "BillingCountry", AVG("Total")
FROM "Invoice"
GROUP BY "BillingCountry"
HAVING AVG("Total") > 5.50;
```
12. List the names of tracks that appear in both the 'Music' playlist and the '90’s Music' playlist.  
```sql
SELECT T1."Name"
FROM "Track" AS T1
JOIN "PlaylistTrack" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Playlist" AS T3 ON T2."PlaylistId" = T3."PlaylistId"
WHERE T3."Name" = 'Music'
INTERSECT
SELECT T1."Name"
FROM "Track" AS T1
JOIN "PlaylistTrack" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Playlist" AS T3 ON T2."PlaylistId" = T3."PlaylistId"
WHERE T3."Name" = '90’s Music';
```
13. How many distinct composers are there in the 'Rock' genre?  
```sql
SELECT COUNT(DISTINCT T1."Composer")
FROM "Track" AS T1
JOIN "Genre" AS T2 ON T1."GenreId" = T2."GenreId"
WHERE T2."Name" = 'Rock';
```
14. Find the total size in bytes of all tracks sold to customers in 'Brazil'. 
```sql
SELECT SUM(T3."Bytes")
FROM "Invoice" AS T1
JOIN "InvoiceLine" AS T2 ON T1."InvoiceId" = T2."InvoiceId"
JOIN "Track" AS T3 ON T2."TrackId" = T3."TrackId"
WHERE T1."BillingCountry" = 'Brazil';
```
15. List the top 5 cities with the highest number of invoices, excluding cities in the USA. 
```sql
SELECT "BillingCity", COUNT("InvoiceId")
FROM "Invoice"
WHERE "BillingCountry" != 'USA'
GROUP BY "BillingCity"
ORDER BY COUNT("InvoiceId") DESC
LIMIT 5;
```
16. Which media type is the most frequent in the 'Classical' playlist?  
```sql
SELECT T4."Name", COUNT(T1."TrackId")
FROM "Track" AS T1
JOIN "PlaylistTrack" AS T2 ON T1."TrackId" = T2."TrackId"
JOIN "Playlist" AS T3 ON T2."PlaylistId" = T3."PlaylistId"
JOIN "MediaType" AS T4 ON T1."MediaTypeId" = T4."MediaTypeId"
WHERE T3."Name" = 'Classical'
GROUP BY T4."Name"
ORDER BY COUNT(T1."TrackId") DESC
LIMIT 1;
```
17. Find the total number of tracks for each album, but only list albums with more than 15 tracks. 
```sql
SELECT T2."Title", COUNT(T1."TrackId")
FROM "Track" AS T1
JOIN "Album" AS T2 ON T1."AlbumId" = T2."AlbumId"
GROUP BY T2."Title"
HAVING COUNT(T1."TrackId") > 15;
```
18. What is the difference in days between the newest and oldest invoice in the database? 
```sql
SELECT MAX("InvoiceDate") - MIN("InvoiceDate")
FROM "Invoice";
```
19. List the names of all tracks that have never been added to any playlist. 
```sql
SELECT T1."Name"
FROM "Track" AS T1
LEFT JOIN "PlaylistTrack" AS T2 ON T1."TrackId" = T2."TrackId"
WHERE T2."PlaylistId" IS NULL;
```
20. Find the customer who has the highest number of individual line items purchased (not total cost, but count of items).  
```sql
SELECT T1."FirstName", T1."LastName", COUNT(T3."InvoiceLineId")
FROM "Customer" AS T1
JOIN "Invoice" AS T2 ON T1."CustomerId" = T2."CustomerId"
JOIN "InvoiceLine" AS T3 ON T2."InvoiceId" = T3."InvoiceId"
GROUP BY T1."CustomerId", T1."FirstName", T1."LastName"
ORDER BY COUNT(T3."InvoiceLineId") DESC
LIMIT 1;
```
