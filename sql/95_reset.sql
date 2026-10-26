DELETE FROM ${vdr}.doc_extracts WHERE file_id IN (SELECT file_id FROM ${vdr}.file_register WHERE deal_room = 'Solace Grid Energy' AND (stage IS NULL OR stage > 1));
DELETE FROM ${vdr}.doc_parsed WHERE file_id IN (SELECT file_id FROM ${vdr}.file_register WHERE deal_room = 'Solace Grid Energy' AND (stage IS NULL OR stage > 1));
DELETE FROM ${vdr}.file_content WHERE file_id IN (SELECT file_id FROM ${vdr}.file_register WHERE deal_room = 'Solace Grid Energy' AND (stage IS NULL OR stage > 1));
DELETE FROM ${vdr}.file_register WHERE deal_room = 'Solace Grid Energy' AND (stage IS NULL OR stage > 1);
