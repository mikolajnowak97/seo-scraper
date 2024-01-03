
class Website:

    def __init__(self, requested_url):
        self.requested_url = requested_url

    def __repr__(self):
        return repr(self.requested_url)

    def insert(self, connection):
        cur = connection.cursor()
        cur.execute(
            """
                INSERT INTO public.websites(requested_url, destination_url, status_code, is_accessible, is_secure, meta_title, meta_robots, meta_canonical, meta_description, ps_desktop_score_best_practices, ps_desktop_score_accessibility, ps_desktop_score_performance, ps_desktop_score_seo, ps_desktop_timing_total, ps_mobile_score_best_practices, ps_mobile_score_accessibility, ps_mobile_score_performance, ps_mobile_score_seo, ps_mobile_timing_total, has_googleanalytics, h1s, h2s)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (
                getattr(self, 'requested_url', None),
                getattr(self, 'destination_url', None),
                getattr(self, 'status_code', None),
                getattr(self, 'is_accessible', None),
                getattr(self, 'is_secure', None),
                getattr(self, 'meta_title', None),
                getattr(self, 'meta_robots', None),
                getattr(self, 'meta_canonical', None),
                getattr(self, 'meta_description', None),
                getattr(self, 'ps_desktop_score_best_practices', None),
                getattr(self, 'ps_desktop_score_accessibility', None),
                getattr(self, 'ps_desktop_score_performance', None),
                getattr(self, 'ps_desktop_score_seo', None),
                getattr(self, 'ps_desktop_timing_total', None),
                getattr(self, 'ps_mobile_score_best_practices', None),
                getattr(self, 'ps_mobile_score_accessibility', None),
                getattr(self, 'ps_mobile_score_performance', None),
                getattr(self, 'ps_mobile_score_seo', None),
                getattr(self, 'ps_mobile_timing_total', None),
                getattr(self, 'has_googleanalytics', None),
                getattr(self, 'h1s', None),
                getattr(self, 'h2s', None),
            ),
        )
        cur.close()
        connection.commit()
