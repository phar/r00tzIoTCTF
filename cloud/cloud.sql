create table homes(
	house_id	text,
	first		text,
	last		text,
	address		text,
	city		text,
	state		text,
	phone		text

);

create table switch_status(
	switch_id	text,
	house_id	text,
	status		integer,
	UNIQUE(switch_id,house_id),
	FOREIGN KEY(house_id) REFERENCES homes(house_id)
);
