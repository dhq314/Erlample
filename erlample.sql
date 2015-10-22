--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: funcs; Type: TABLE; Schema: public; Owner: erlample; Tablespace:
--

CREATE TABLE funcs (
    id integer NOT NULL,
    name character varying(80) DEFAULT ''::character varying NOT NULL,
    mid integer NOT NULL,
    html text NOT NULL,
    describe text,
    usage character varying(100) DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.funcs OWNER TO erlample;

--
-- Name: funcs_id_seq; Type: SEQUENCE; Schema: public; Owner: erlample
--

CREATE SEQUENCE funcs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.funcs_id_seq OWNER TO erlample;

--
-- Name: funcs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: erlample
--

ALTER SEQUENCE funcs_id_seq OWNED BY funcs.id;


--
-- Name: mod; Type: TABLE; Schema: public; Owner: erlample; Tablespace:
--

CREATE TABLE mod (
    id integer NOT NULL,
    name character varying(80) DEFAULT ''::character varying NOT NULL,
    describe text NOT NULL,
    html text
);


ALTER TABLE public.mod OWNER TO erlample;

--
-- Name: mod_id_seq; Type: SEQUENCE; Schema: public; Owner: erlample
--

CREATE SEQUENCE mod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mod_id_seq OWNER TO erlample;

--
-- Name: mod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: erlample
--

ALTER SEQUENCE mod_id_seq OWNED BY mod.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: erlample
--

ALTER TABLE ONLY funcs ALTER COLUMN id SET DEFAULT nextval('funcs_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: erlample
--

ALTER TABLE ONLY mod ALTER COLUMN id SET DEFAULT nextval('mod_id_seq'::regclass);


--
-- Name: funcs_pkey; Type: CONSTRAINT; Schema: public; Owner: erlample; Tablespace:
--

ALTER TABLE ONLY funcs
    ADD CONSTRAINT funcs_pkey PRIMARY KEY (id);


--
-- Name: mod_pkey; Type: CONSTRAINT; Schema: public; Owner: erlample; Tablespace:
--

ALTER TABLE ONLY mod
    ADD CONSTRAINT mod_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: erlample
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM erlample;
GRANT ALL ON SCHEMA public TO erlample;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

