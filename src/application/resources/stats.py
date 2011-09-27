# encoding: utf-8


import simplejson as json
from resource import Resource
from flask import Response, request, jsonify, abort
from google.appengine.ext.db import Key

from application.models import Report, StatsStore
from application.ee import Stats

from google.appengine.api import memcache

tables = [
    ('Municipalities', 1560866, 'name'),
    ('States', 1560836, 'name'),
    ('Federal Conservation', 1568452, 'name'),
    ('State Conservation', 1568376, 'name'),
    ('Ingienous Land',1630610, 'name'),
    ('Legal Amazon', 1205151, 'name')
]


class RegionStatsAPI(Resource):
    """ serves stats for regions

        basically is a proxy for google earth engine
    """

    def stats_for(self, r, table):
        st = Stats()
        return st.get_stats(r.base_map(),  table)

    # TODO: change for get
    def list(self, report_id):
        cache_key = 'stats_' + report_id
        data = memcache.get(cache_key)
        if not data:
            r = Report.get(Key(report_id))
            if not r:
                abort(404)
            #TODO: get from datastore
            stats = {
                'id': report_id,
                'stats': {}
            }
            for desc, table, name in tables:
                stats['stats'].update(self.stats_for(r, table))
            # cache it
            data = json.dumps(stats)
            memcache.set(cache_key, data)
            # save it!
            StatsStore(report=r, json=data).put()
        return Response(data, mimetype='application/json')

