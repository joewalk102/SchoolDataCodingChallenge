## Notes on implementation
If I were to implement this in a production environment, there are a couple
things I would change. For instance, if the pattern of access would be to 
process once and access the results regularly, I would break out the ingestion from
the rest of the program, and, depending on the rate of change of the source
data, I would most likely set it up as a CRON or scheduled job. This could allow
an easy daily/monthly/yearly update of the data as new data became available.

If the intent for the statistical results was to be accessed regularly, ingesting
the data into a database would probably be the best approach, along with some
shortcuts (such as storing pre-processed fields, like the count, so that 
the field in the database could be accessed at-will, instead of having to 
re-compute everything each time). This "caching" of values would have to be balanced
between quick access and storage constraints and concerns.

Another significant change could be to implement multi-processing for the ingestion
phase. This could greatly speed up the ingestion process, but may only be worth the
effort if the source data changes on a frequent basis (requiring a re-calculation
of the metrics from the ground-up). If the data only changes on a (say) yearly basis,
then the 5 minutes it takes to ingest the data for the entire year would be insignificant
and probably not worth the complexity of maintaining a parallel-ized program. 
