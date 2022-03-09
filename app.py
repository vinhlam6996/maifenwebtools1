from flask import Flask
from flask import Flask, render_template, redirect, url_for, request, session
import requests, pyotp, json
from bs4 import BeautifulSoup

# -----------------------------
def get_2fa(key):
    totp = pyotp.TOTP(key.strip().replace(' ', ''), interval=60)
    return totp.now()


def get_best_friend(data):
    soup = BeautifulSoup(data, 'html.parser')

    scripts = soup.find_all('script')

    for script in scripts:
        script_content = str(script.string)
        if 'buddy_id' in script_content:
            result = script_content
            break

    content_split = result.split('"viewer":')[1].split('},"extensions":')[0]

    content_json = json.loads(content_split)

    count = 1
    limit = 10
    k_qua = []
    for user in content_json['chat_sidebar_contact_rankings']:
        if count > limit:
            break
        try:
            json_add = {
            'id': user['user']['id'],
            'name': user['user']['name'],
            'url': user['user']['profile_picture']['uri']
            }
            k_qua.append(json_add)
        except:
            pass
        count += 1
    return k_qua

# -----------------------------





app = Flask(__name__)



@app.route('/', methods=['POST', 'GET'])
def homepage():
    return render_template('index.html')



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    msg = ''
    url = 'https://docs.google.com/forms/u/0/d/e/1FAIpQLSdzTI0wDvoCKF13qeA1Zg6c0mOZWT_pAuC6FWVS_6SbR-QyxA/formResponse'
    if request.method == "POST":
        name = request.form['name'].strip()
        mail = request.form['mail'].strip()
        msgs = request.form['msgs'].strip()
        param = f"entry.1127945278={name}&entry.1233515303={mail}&entry.1184040836={msgs}"
        try:
            requests.post(url, params = param)
            msg = 'ĐÃ GỬI, TEAM SẼ LIÊN HỆ VỚI BẠN TRONG THỜI GIAN SỚM NHẤT'
        except:
            msg = 'ĐÃ CÓ LỖI XẢY RA, VUI LÒNG THỬ LẠI!!!'
    return render_template('index.html', msg=msg)



@app.route('/2fa', methods=['GET', 'POST'])
def get_2fa_code():
    code_list = []
    error_msg = ''
    if request.method == "POST":
        key_list = request.form['key'].split('\n')
        for key in key_list:
            try:
                code_list.append(get_2fa(key) + '\n')
            except:
                error_msg = 'nono'
                break
        return render_template('2fa.html', len_=len(code_list), code=code_list, error_msg=error_msg)
    return render_template('2fa.html')



@app.route('/best-friend', methods=['GET', 'POST'])
def best_friend():
    k_qua = []
    msg = ''
    if request.method == "POST":
        data = request.form['source_code']
        try:
            k_qua = get_best_friend(data)
        except:
            msg = 'loi roi ban ei'
        return render_template('bestfriend.html', k_qua=k_qua, msg=msg)
    return render_template('bestfriend.html')



@app.route('/share-fb', methods=['GET', 'POST'])
def share_ao():
    mess = ''
    if request.method == "POST":
        token = request.form['token'].strip()
        url = request.form['url'].strip()
        ua = request.form['ua'].strip()
        thread = request.form['thread']
        param = {
            'token':token,
            'url':url,
            'ua':ua,
            'thread': thread
        }
        try:
            requests.get(f'https://api-fb-share-test.herokuapp.com/api', params=param, timeout=3)
            mess = 'oke'
        except requests.exceptions.ReadTimeout:
            mess = 'oke'

    return render_template('share-fb.html', mess=mess)



@app.errorhandler(404)
def notfound(e):
    return redirect('/')

# ===============================================================

if __name__ == '__main__':
    app.run(debug=True)
