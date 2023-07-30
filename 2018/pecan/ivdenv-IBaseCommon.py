
class IBaseCommon(object):
    def __init__(self, db_table):
        self.db_table = db_table

    def parse_filter(self, cond):
        LOG.debug(cond)
        if cond == 'and' or cond == 'or':
            return cond
        if '::' in cond:
            (key, value) = cond.split('::')
            ct = get_column_type(self.db_table.__tablename__, key)
            if str(ct) == 'VARCHAR':
                return '%s.%s == "%s"' % (self.db_table.__tablename__, key, value)
            else:
                return '%s.%s == %s' % (self.db_table.__tablename__, key, value)
        else:
            (key, value) = cond.split(':')
            ct = get_column_type(self.db_table.__tablename__, key)
            if value[0] == '^':
                if str(ct) == 'VARCHAR':
                    return '%s.%s != "%s"' % (self.db_table.__tablename__, key, value)
                else:
                    return '%s.%s != %s' % (self.db_table.__tablename__, key, value)
            else:
                if value[0] == '(':
                    (start, end) = value[1:-1].split(',')
                    if value[-1] == ')':
                        op = '<'
                    else:
                        op = '<='

                    if not start and end:
                        return '%s.%s %s %s' % (
                            self.db_table.__tablename__, key, op, end)
                    if not end and start:
                        return '%s.%s > %s' % (
                            self.db_table.__tablename__, key, start)
                    if not start and not end:
                        LOG.debug('invalid filter' + cond)
                        abort(500)
                    if start and end:
                        return '%s.%s > %s and %s.%s %s %s' % (
                            self.db_table.__tablename__, key, start,
                            self.db_table.__tablename__, key, op, end)
                else:
                    return '%s.%s like "%s"' % (self.db_table.__tablename__, key, '%' + value + '%')

    def filter(self, query, condition):
        # conds = re.split(r'/&', condition)
        # if conds[0] == str(condition):
        #     conds = re.split(r'\s*and\s*', condition)
        conds = re.split(r'\s*and\s*', condition)
        LOG.info(conds)
        LOG.info(type(conds))
        conds = map(self.parse_filter, conds)
        LOG.debug(' '.join(conds))
        return query.filter(text(' and '.join(conds)))

    def assoc_query(self, query, assoc_type, assoc_id):
        assoc_table = get_table_class(assoc_type)
        LOG.debug(assoc_table)
        return query.join(assoc_table).filter(assoc_table.ID == assoc_id)

    def sort(self, query, condition):
        (column, direction) = condition.split(',')
        if direction == 'd':
            LOG.debug('sort desc')
            return query.order_by(desc(getattr(self.db_table, column)))
        else:
            LOG.debug('sort asc')
            return query.order_by(asc(getattr(self.db_table, column)))

    def range(self, condition):
        (start, end) = condition[1:-1].split('-')
        return start, end

    def query(self, **kwargs):
        LOG.debug(repr(kwargs))
        filter_cond = kwargs.pop('filter', None)
        order_cond = kwargs.pop('sortby', None)
        range_cond = kwargs.pop('range', None)
        assoc_type = kwargs.pop('ASSOCIATEOBJTYPE', None)
        LOG.debug([("filter_cond: ", filter_cond), ("order_cond: ", order_cond), ("range_cond: ", range_cond), ("assoc_type: ", assoc_type)])
        assoc_id = kwargs.pop('ASSOCIATEOBJID', None)

        query = db_session.query(self.db_table)
        if assoc_type and assoc_id:
            query = self.assoc_query(query, assoc_type, assoc_id)

        if filter_cond:
            query = self.filter(query, filter_cond)

        for (k, v) in kwargs.items():
            LOG.debug('filter key: %s, value:%s' % (k, v))
            ct = get_column_type(self.db_table.__tablename__, k)
            if str(ct) == 'VARCHAR':
                cond = '%s.%s == "%s"' % (self.db_table.__tablename__, k, v)
            else:
                cond = '%s.%s == %s' % (self.db_table.__tablename__, k, v)
            query = query.filter(text(cond))

        if order_cond:
            query = self.sort(query, order_cond)
        if range_cond:
            (start, end) = self.range(range_cond)
            if end:
                data = query.all()[int(start):int(end)]
            else:
                data = query.all()[int(start)]

        else:
            data = query.all()

        return data

    def get(self, **kwargs):
        data = self.query(**kwargs)
        filter_cond = kwargs.pop('filter', None)
        if len(data) == 0 and filter_cond:
            return {"error": {"code": 0, "description": "0"}}
            # return {"data": [], "error": {"code": 0, "description": "0"}}
        else:
            return model.ibase_jsonify(data)

    def count(self, **kwargs):
        return model.ibase_jsonify({'COUNT': len(self.query(**kwargs))})



