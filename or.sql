--
-- PostgreSQL database dump
--

-- Dumped from database version 14.2
-- Dumped by pg_dump version 14.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: observing; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.observing (
    year integer NOT NULL,
    condition character varying(20) NOT NULL,
    needs_attention boolean,
    animal_chip integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.observing OWNER TO postgres;

--
-- Name: wild_life; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wild_life (
    chip_number integer NOT NULL,
    kingdom character varying(20) NOT NULL,
    division character varying(20) NOT NULL,
    class character varying(20) NOT NULL,
    "order" character varying(20) NOT NULL,
    family character varying(20) NOT NULL,
    genus character varying(20) NOT NULL,
    species character varying(20) NOT NULL,
    biologist character varying(30),
    country character varying(20),
    sex character(1)
);


ALTER TABLE public.wild_life OWNER TO postgres;

--
-- Data for Name: observing; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.observing (year, condition, needs_attention, animal_chip, id) FROM stdin;
2021	healthy	t	138778	4
2020	injured	t	139625	5
2021	healthy	t	139625	6
2020	pregnant	f	127863	1
2020	healthy	f	138778	3
2020	healty	f	149652	7
2021	pregnant	t	149652	8
2020	ill	t	152649	9
2021	demise	f	152649	10
2020	pregnant	f	154762	11
2021	pregnant	f	154762	12
2020	injured	t	159426	13
2021	demise	f	159426	14
2021	healthy	f	127863	2
2020	healthy	f	163284	15
2021	healthy	f	163284	16
2020	healthy	f	167954	17
2021	demise	f	167954	18
2020	injures	t	168349	19
2021	healthy	f	168349	20
2020	healthy	f	184759	21
2021	demise	f	184759	22
\.


--
-- Data for Name: wild_life; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wild_life (chip_number, kingdom, division, class, "order", family, genus, species, biologist, country, sex) FROM stdin;
138778	Animalia	Chordata	Mammalia	Carnivora	Felidae	Panthera	P. leo	Jonathan Snow	Burkina Faso	M
149652	Animalia	Chordata	Mammalia	Carnivora	Felidae	Panthera	P. leo	Johnatan Snow	Congo	F
139625	Animalia	Chordata	Mammalia	Pilosa	Bradypodidae	Bradypus	B. variegatus	Maria Barros	Brasil	F
127863	Animalia	Chordata	Amphibia	Caudata	Proteidae	Proteus	P. anguinus	Ivan Horvat	Croatia	F
159426	Animalia	Chordata	Chrondrichthyes	Lamniformes	Lamnidae	Carcharodon	C. carcharias	Matt Smith	USA	M
152649	Animalia	Chordata	Amphibia	Anura	Bufonidae	Bufo	B. viridis	Jan Težak	Slovenia	M
184759	Animalia	Arthropoda	Insecta	Lepidoptera	Lycaenidae	Lycaena	L. alciphron	Petar Jovanić	Serbia	M
163284	Animalia	Chordata	Mammaila	Diprotodontia	Phascolarctidae	Phascolarctos	P. cinereus	Harry White	Australia	F
154762	Animalia	Chordata	Mammalia	Proboscidea	Elephantidae	Elephas	E. maximus	Lars Andersson	Zimbabwe	F
167954	Animalia	Chordata	Reptilia	Testudines	Trionychidae	Pelochelys	P. cantorii	Hanh Gnuyen	Vietnam	M
168349	Animalia	Chordata	Aves	Galliformes	Phasianidae	Pavo	P. cristatus	Abishek Laghari	India	M
\.


--
-- Name: observing observing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.observing
    ADD CONSTRAINT observing_pkey PRIMARY KEY (id);


--
-- Name: wild_life wild_life_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wild_life
    ADD CONSTRAINT wild_life_pkey PRIMARY KEY (chip_number);


--
-- Name: fki_divlje_zivotinje; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_divlje_zivotinje ON public.observing USING btree (animal_chip);


--
-- Name: observing divlje_zivotinje; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.observing
    ADD CONSTRAINT divlje_zivotinje FOREIGN KEY (animal_chip) REFERENCES public.wild_life(chip_number) NOT VALID;


--
-- PostgreSQL database dump complete
--

