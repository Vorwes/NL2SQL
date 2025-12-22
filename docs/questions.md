# **Easy Level:**
1. Show all the countries where customers live. 
```sql
SELECT DISTINCT country FROM customer;
```
2. Show all the countries where customers live. 
```sql
SELECT title FROM album;
```
3. Find the first and last names of all employees who are Sales Support Agents. 
```sql
SELECT first_name, last_name FROM employee WHERE title = 'Sales Support Agent';
```
4. What are the names of all the musical genres?  
```sql
SELECT name FROM genre;
```
5. How many total tracks are there in the database?  
```sql
SELECT COUNT(*) FROM track;
```
6. Show the customers who live in Brazil. 
```sql
SELECT * FROM customer WHERE country = 'Brazil';
```
7. Find the name of the artist with the Artist ID of 50.  
```sql
SELECT name FROM artist WHERE artist_id = 50;
```
8. List all invoices where the total amount is greater than 10 dollars. 
```sql
SELECT * FROM invoice WHERE total > 10;
```
9. Show the list of tracks ordered by their length in milliseconds from longest to shortest.  
```sql
SELECT name, milliseconds FROM track ORDER BY milliseconds DESC;
```
10. What is the total number of distinct customers in the Invoice table? 
```sql
SELECT COUNT(DISTINCT customer_id) FROM invoice;
```
# **Medium Level:**
1. Show the list of all album titles along with the name of the artist who created them.  
```sql
SELECT T1.title, T2.name
FROM album AS T1
JOIN artist AS T2 ON T1.artist_id = T2.artist_id;
```
2.Find the first and last names of all customers and the first and last name of their assigned support agent. 
```sql
SELECT T1.first_name, T1.last_name, T2.first_name AS agent_first_name, T2.last_name AS agent_last_name
FROM customer AS T1
JOIN employee AS T2 ON T1.support_rep_id = T2.employee_id;
```
3. List the names of all tracks that belong to the 'Rock' genre.  
```sql
SELECT T1.name
FROM track AS T1
JOIN genre AS T2 ON T1.genre_id = T2.genre_id
WHERE T2.name = 'Rock';
```
4. Show the total amount of money spent by the customer named 'Mark Taylor'.  
```sql
SELECT SUM(T1.total)
FROM invoice AS T1
JOIN customer AS T2 ON T1.customer_id = T2.customer_id
WHERE T2.first_name = 'Mark' AND T2.last_name = 'Taylor';
```
5. How many albums does the artist 'Led Zeppelin' have in the database?   
```sql
SELECT COUNT(*)
FROM album AS T1
JOIN artist AS T2 ON T1.artist_id = T2.artist_id
WHERE T2.name = 'Led Zeppelin';
```
6. List all the track names and the name of the media type for each track.   
```sql
SELECT T1.name, T2.name AS media_type
FROM track AS T1
JOIN media_type AS T2 ON T1.media_type_id = T2.media_type_id;
```
7. Show the total number of tracks available for each genre name.  
```sql
SELECT T2.name, COUNT(T1.track_id)
FROM track AS T1
JOIN genre AS T2 ON T1.genre_id = T2.genre_id
GROUP BY T2.name;
```
8. List the details of all invoices (Invoice ID and Date) for customers living in 'France'.   
```sql
SELECT T1.invoice_id, T1.invoice_date
FROM invoice AS T1
JOIN customer AS T2 ON T1.customer_id = T2.customer_id
WHERE T2.country = 'France';
```
9. Find the names of all tracks in the playlist named 'Classical'. 
```sql
SELECT T1.name
FROM track AS T1
JOIN playlist_track AS T2 ON T1.track_id = T2.track_id
JOIN playlist AS T3 ON T2.playlist_id = T3.playlist_id
WHERE T3.name = 'Classical';
```
10.  Who are the top 5 artists with the most albums? 
```sql
SELECT T2.name, COUNT(T1.album_id)
FROM album AS T1
JOIN artist AS T2 ON T1.artist_id = T2.artist_id
GROUP BY T2.name
ORDER BY COUNT(T1.album_id) DESC
LIMIT 5;
```
11. List the names of all tracks included in the album 'Let There Be Rock'. 
```sql
SELECT T1.name
FROM track AS T1
JOIN album AS T2 ON T1.album_id = T2.album_id
WHERE T2.title = 'Let There Be Rock';
```
12. Find the full names of customers supported by the agent 'Margaret Park'. 
```sql
SELECT T1.first_name, T1.last_name
FROM customer AS T1
JOIN employee AS T2 ON T1.support_rep_id = T2.employee_id
WHERE T2.first_name = 'Margaret' AND T2.last_name = 'Park';
```
13. Calculate the total quantity of items sold in Invoice ID 1.
```sql
SELECT SUM(quantity)
FROM invoice_line
WHERE invoice_id = 1;
```
14. Show the names of all tracks in the playlist 'Heavy Metal Classic'. 
```sql
SELECT T1.name
FROM track AS T1
JOIN playlist_track AS T2 ON T1.track_id = T2.track_id
JOIN playlist AS T3 ON T2.playlist_id = T3.playlist_id
WHERE T3.name = 'Heavy Metal Classic';
```
15. Find the total amount spent by the customer 'Leonie Köhler'. 
```sql
SELECT SUM(T1.total)
FROM invoice AS T1
JOIN customer AS T2 ON T1.customer_id = T2.customer_id
WHERE T2.first_name = 'Leonie' AND T2.last_name = 'Köhler';
```
16. How many tracks belong to the 'Latin' genre? 
```sql
SELECT COUNT(T1.track_id)
FROM track AS T1
JOIN genre AS T2 ON T1.genre_id = T2.genre_id
WHERE T2.name = 'Latin';
```
17. What is the average duration (in milliseconds) of tracks in the 'Jazz' genre? 
```sql
SELECT AVG(T1.milliseconds)
FROM track AS T1
JOIN genre AS T2 ON T1.genre_id = T2.genre_id
WHERE T2.name = 'Jazz';
```
18. List the tracks composed by 'Miles Davis' that are also in the 'Jazz' genre.  
```sql
SELECT T1.name
FROM track AS T1
JOIN genre AS T2 ON T1.genre_id = T2.genre_id
WHERE T1.composer = 'Miles Davis' AND T2.name = 'Jazz';
```
19. Show the first and last names of employees who report to 'Andrew Adams'.  
```sql
SELECT T1.first_name, T1.last_name
FROM employee AS T1
JOIN employee AS T2 ON T1.reports_to = T2.employee_id
WHERE T2.first_name = 'Andrew' AND T2.last_name = 'Adams';
```
20. List the 5 shortest tracks in the database.  
```sql
SELECT name, milliseconds
FROM track
ORDER BY milliseconds ASC
LIMIT 5;
```
21. Find the total revenue generated from invoices billed to the city 'Paris'. 
```sql
SELECT SUM(total)
FROM invoice
WHERE billing_city = 'Paris';
```
22. List all artist names along with the number of albums they have released. 
```sql
SELECT T2.name, COUNT(T1.album_id)
FROM album AS T1
JOIN artist AS T2 ON T1.artist_id = T2.artist_id
GROUP BY T2.name;
```
23. Find the names of all tracks with the media type 'Purchased AAC audio file'.  
```sql
SELECT T1.name
FROM track AS T1
JOIN media_type AS T2 ON T1.media_type_id = T2.media_type_id
WHERE T2.name = 'Purchased AAC audio file';
```
24. List the Invoice ID and Total for all invoices where the customer lives in 'Canada'.  
```sql
SELECT T1.invoice_id, T1.total
FROM invoice AS T1
JOIN customer AS T2 ON T1.customer_id = T2.customer_id
WHERE T2.country = 'Canada';
```
25. Count the total number of invoices issued to customers in the 'USA'. 
```sql
SELECT COUNT(T1.invoice_id)
FROM invoice AS T1
JOIN customer AS T2 ON T1.customer_id = T2.customer_id
WHERE T2.country = 'USA';
```
26. List the distinct genre names present in the playlist named '90’s Music'. 
```sql
SELECT DISTINCT T3.name
FROM playlist_track AS T1
JOIN track AS T2 ON T1.track_id = T2.track_id
JOIN genre AS T3 ON T2.genre_id = T3.genre_id
JOIN playlist AS T4 ON T1.playlist_id = T4.playlist_id
WHERE T4.name = '90’s Music';
```
27. Calculate the total price (sum of UnitPrice) of all tracks in the album 'Greatest Hits'.  
```sql
SELECT SUM(T1.unit_price)
FROM track AS T1
JOIN album AS T2 ON T1.album_id = T2.album_id
WHERE T2.title = 'Greatest Hits';
```
28. List the full names of employees hired in the year 2002. 
```sql
SELECT first_name, last_name
FROM employee
WHERE hire_date BETWEEN '2002-01-01' AND '2002-12-31';
```
29. Find the name of the artist who performed the track 'Put The Finger On You'. 
```sql
SELECT T2.name
FROM track AS T1
JOIN album AS T3 ON T1.album_id = T3.album_id
JOIN artist AS T2 ON T3.artist_id = T2.artist_id
WHERE T1.name = 'Put The Finger On You';
```
30. Show the total sum of invoice totals where the billing country is 'India'.
```sql
SELECT SUM(total)
FROM invoice
WHERE billing_country = 'India';
```
# **Hard Level:**
1. Find the names of all customers who have purchased a track from the 'Rock' genre. 
```sql
SELECT DISTINCT T1.first_name, T1.last_name
FROM customer AS T1
JOIN invoice AS T2 ON T1.customer_id = T2.customer_id
JOIN invoice_line AS T3 ON T2.invoice_id = T3.invoice_id
JOIN track AS T4 ON T3.track_id = T4.track_id
JOIN genre AS T5 ON T4.genre_id = T5.genre_id
WHERE T5.name = 'Rock';
```
2. Which artist has earned the most money from sales? 
```sql
SELECT T3.name, SUM(T2.unit_price * T2.quantity) AS total_sales
FROM track AS T1
JOIN invoice_line AS T2 ON T1.track_id = T2.track_id
JOIN album AS T4 ON T1.album_id = T4.album_id
JOIN artist AS T3 ON T4.artist_id = T3.artist_id
GROUP BY T3.name
ORDER BY total_sales DESC
LIMIT 1;
```
3. List the titles of all albums that have tracks sold in the USA. 
```sql
SELECT DISTINCT T3.title
FROM invoice AS T1
JOIN invoice_line AS T2 ON T1.invoice_id = T2.invoice_id
JOIN track AS T4 ON T2.track_id = T4.track_id
JOIN album AS T3 ON T4.album_id = T3.album_id
WHERE T1.billing_country = 'USA';
```
4. Find the first and last name of the employee who supports the customer with the highest total payments. 
```sql
SELECT T1.first_name, T1.last_name
FROM employee AS T1
JOIN customer AS T2 ON T1.employee_id = T2.support_rep_id
ORDER BY (SELECT SUM(total) FROM invoice WHERE customer_id = T2.customer_id) DESC
LIMIT 1;
```
5. Which countries have more than 5 customers? 
```sql
SELECT country, COUNT(customer_id)
FROM customer
GROUP BY country
HAVING COUNT(customer_id) > 5;
```
6. List all tracks that are longer than the average track duration of the entire database. 
```sql
SELECT name, milliseconds
FROM track
WHERE milliseconds > (SELECT AVG(milliseconds) FROM track);
```
7. Find the names of artists who have never sold a track. 
```sql
SELECT T1.name
FROM artist AS T1
LEFT JOIN album AS T2 ON T1.artist_id = T2.artist_id
LEFT JOIN track AS T3 ON T2.album_id = T3.album_id
LEFT JOIN invoice_line AS T4 ON T3.track_id = T4.track_id
WHERE T4.invoice_line_id IS NULL;
```
8. Show the top 3 most popular genres based on the number of tracks sold. 
```sql
SELECT T3.name, COUNT(T2.invoice_line_id)
FROM track AS T1
JOIN invoice_line AS T2 ON T1.track_id = T2.track_id
JOIN genre AS T3 ON T1.genre_id = T3.genre_id
GROUP BY T3.name
ORDER BY COUNT(T2.invoice_line_id) DESC
LIMIT 3;
```
9. List the names of all employees who are older than their manager. 
```sql
SELECT T1.first_name, T1.last_name
FROM employee AS T1
JOIN employee AS T2 ON T1.reports_to = T2.employee_id
WHERE T1.birth_date < T2.birth_date;
```
10. Find the customer who has spent the most on music by the artist 'Iron Maiden'. 
```sql
SELECT T1.first_name, T1.last_name, SUM(T3.unit_price * T3.quantity) AS spent
FROM customer AS T1
JOIN invoice AS T2 ON T1.customer_id = T2.customer_id
JOIN invoice_line AS T3 ON T2.invoice_id = T3.invoice_id
JOIN track AS T4 ON T3.track_id = T4.track_id
JOIN album AS T5 ON T4.album_id = T5.album_id
JOIN artist AS T6 ON T5.artist_id = T6.artist_id
WHERE T6.name = 'Iron Maiden'
GROUP BY T1.customer_id, T1.first_name, T1.last_name
ORDER BY spent DESC
LIMIT 1;
```
11. Calculate the average invoice total for each country, but only show countries where the average is greater than $5.50. 
```sql
SELECT billing_country, AVG(total)
FROM invoice
GROUP BY billing_country
HAVING AVG(total) > 5.50;
```
12. List the names of tracks that appear in both the 'Music' playlist and the '90’s Music' playlist.  
```sql
SELECT T1.name
FROM track AS T1
JOIN playlist_track AS T2 ON T1.track_id = T2.track_id
JOIN playlist AS T3 ON T2.playlist_id = T3.playlist_id
WHERE T3.name = 'Music'
INTERSECT
SELECT T1.name
FROM track AS T1
JOIN playlist_track AS T2 ON T1.track_id = T2.track_id
JOIN playlist AS T3 ON T2.playlist_id = T3.playlist_id
WHERE T3.name = '90’s Music';
```
13. How many distinct composers are there in the 'Rock' genre?  
```sql
SELECT COUNT(DISTINCT T1.composer)
FROM track AS T1
JOIN genre AS T2 ON T1.genre_id = T2.genre_id
WHERE T2.name = 'Rock';
```
14. Find the total size in bytes of all tracks sold to customers in 'Brazil'. 
```sql
SELECT SUM(T3.bytes)
FROM invoice AS T1
JOIN invoice_line AS T2 ON T1.invoice_id = T2.invoice_id
JOIN track AS T3 ON T2.track_id = T3.track_id
WHERE T1.billing_country = 'Brazil';
```
15. List the top 5 cities with the highest number of invoices, excluding cities in the USA. 
```sql
SELECT billing_city, COUNT(invoice_id)
FROM invoice
WHERE billing_country != 'USA'
GROUP BY billing_city
ORDER BY COUNT(invoice_id) DESC
LIMIT 5;
```
16. Which media type is the most frequent in the 'Classical' playlist?  
```sql
SELECT T4.name, COUNT(T1.track_id)
FROM track AS T1
JOIN playlist_track AS T2 ON T1.track_id = T2.track_id
JOIN playlist AS T3 ON T2.playlist_id = T3.playlist_id
JOIN media_type AS T4 ON T1.media_type_id = T4.media_type_id
WHERE T3.name = 'Classical'
GROUP BY T4.name
ORDER BY COUNT(T1.track_id) DESC
LIMIT 1;
```
17. Find the total number of tracks for each album, but only list albums with more than 15 tracks. 
```sql
SELECT T2.title, COUNT(T1.track_id)
FROM track AS T1
JOIN album AS T2 ON T1.album_id = T2.album_id
GROUP BY T2.title
HAVING COUNT(T1.track_id) > 15;
```
18. What is the difference in days between the newest and oldest invoice in the database? 
```sql
SELECT MAX(invoice_date) - MIN(invoice_date)
FROM invoice;
```
19. List the names of all tracks that have never been added to any playlist. 
```sql
SELECT T1.name
FROM track AS T1
LEFT JOIN playlist_track AS T2 ON T1.track_id = T2.track_id
WHERE T2.playlist_id IS NULL;
```
20. Find the customer who has the highest number of individual line items purchased (not total cost, but count of items).  
```sql
SELECT T1.first_name, T1.last_name, COUNT(T3.invoice_line_id)
FROM customer AS T1
JOIN invoice AS T2 ON T1.customer_id = T2.customer_id
JOIN invoice_line AS T3 ON T2.invoice_id = T3.invoice_id
GROUP BY T1.customer_id, T1.first_name, T1.last_name
ORDER BY COUNT(T3.invoice_line_id) DESC
LIMIT 1;
```
