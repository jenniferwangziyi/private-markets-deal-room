CREATE CATALOG IF NOT EXISTS ${catalog};
CREATE SCHEMA IF NOT EXISTS ${vdr};
CREATE SCHEMA IF NOT EXISTS ${semantic};
CREATE SCHEMA IF NOT EXISTS ${governance};
CREATE VOLUME IF NOT EXISTS ${vdr}.deal_rooms COMMENT 'Deal-room landing zone (Phase A/B/C folders); SharePoint is synced alongside';
CREATE VOLUME IF NOT EXISTS ${vdr}.portal_uploads COMMENT 'External-party portal uploads';
