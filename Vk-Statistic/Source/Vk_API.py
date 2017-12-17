import vk
import datetime
from time import sleep


class MakeAPiConnect:
    def init_token(self, token):
        try:
            if token:
                self.session = vk.Session(access_token=token)
                self.vk_api = vk.API(self.session)
                return True
            return False
        except Exception as invalid_token_error:
            return False

    def init_login(self, APP_ID, login, password):
        try:
            self.session = vk.AuthSession(app_id=APP_ID, user_login=login, user_password=password,
                                        scope='wall, messages, friends, groups')
            self.vk_api = vk.API(session)  # self.session
            return True
        except Exception as invalid_data_error:
            return False

    def delete_msgs(self, dialogs):
        for i in dialogs[1:]:
            self.vk_api.messages.deleteDialog(user_id=i['uid'])
            sleep(0.2)  # it's a bad practise to use sleep, try to use async

    def collect_dialogs(self):
        return self.vk_api.messages.getDialogs(count=200)

    def clear_wall(self, posts):
        for post in posts[1:]:
            self.vk_api.wall.delete(post_id=post['id'])
            sleep(0.2)

    def collect_wall(self):
        return self.vk_api.wall.get()

    def delete_groups(self, groups):
        for i in groups[1:]:
            self.vk_api.groups.leave(group_id=i)
            sleep(0.2)

    def collect_all_groups(self):
        return self.vk_api.groups.get(count=1000)

    def delete_friends(self, friends):
        for i in friends:
            self.vk_api.friends.delete(user_id=i['uid'])
            sleep(0.2)

    def collect_all_friends(self):
        return self.vk_api.friends.get(fields='city')

    def get_user(self, uid):
        return self.vk_api.users.get(user_ids=int(uid), fields='counters, last_seen, online, bdate, city, country, has_photo')

    def collect_friends(self):
        current_year = datetime.datetime.now().year
        me = self.vk_api.users.get(fields='sex, bdate, education, city')[0]
        all_friends = self.vk_api.friends.get(fields='sex, bdate, education, city')

        friends_count = len(all_friends)
        men = list(filter(lambda x: x.get('sex') and x['sex'] == 2, all_friends))
        women = list(filter(lambda x: x.get('sex') and x['sex'] == 1, all_friends))
        online = list(filter(lambda x: x.get('online') and x['online'] == 1, all_friends))
        cob = list(filter(lambda x: x.get('city') and me.get('city') and x['city'] == me['city'], all_friends))
        classmates = list(filter(lambda x: x.get('university') and me.get('university') and x['university'] == me[0]['university'] and any((x['university'], me[0]['university'])), all_friends))   
        age = [current_year - int(x['bdate'].split('.')[-1]) for x in all_friends if x.get('bdate') and len(x['bdate'].split('.')) == 3]

        result = {
            'men': men,
            'women': women,
            'online': online,
            'cob': cob,
            'classmates': classmates,
            'friends_count': friends_count,
            'age': age
        }
        return result  # try to return without additional variable
