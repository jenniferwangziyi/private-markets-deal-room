SELECT current_user() AS who,
       (SELECT count(*) FROM ${vdr}.investments) AS investments,
       (SELECT count(DISTINCT portfolio) FROM ${vdr}.investments) AS portfolios;
