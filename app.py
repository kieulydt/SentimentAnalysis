from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
import requests
import pandas as pd
from datetime import datetime, date, time, timezone



app = Flask(__name__)
text = None
data = None
file = None

@app.route('/')
def home():
    return render_template('index.html', data=None, text='', file=None)

@app.route('/send', methods=['POST'])
def sent():
    """Nhận 1 câu miêu tả và phân tích"""
    if request.method == 'POST':
        global text
        global data
        text = request.form['text']
        apiURL = 'http://124.158.1.125:8807/sentiment?text=' + text
        f = requests.get(apiURL)
        data = list(f.json())
        for i in range(len(data)):
            if data[i]['result'] == 'positive':
                data[i]['positive'] = float(data[i]['score'])
                data[i]['negative'] = round(1 - data[i]['positive'], 3)
            if data[i]['result'] == 'negative':
                data[i]['negative'] = float(data[i]['score'])
                data[i]['positive'] = round(1 - data[i]['negative'], 3)
        # Test
        print(data)
        print(text)
        return render_template('index.html', data=data, text=text, file=None)

@app.route('/upload', methods=['POST'])
def process_file():
    """Nhận dữ liệu là 1 file csv"""
    if request.method == 'POST':
        f = request.files['file']
        time_sub = str(datetime.now())
        time_sub = time_sub.replace("-", "").replace(" ", "").replace(":","").replace(".","")
        print(time_sub)
        f.save('./files/' + time_sub + '.csv')
        csv = pd.read_csv('./files/' + f.filename)
        cols = ['TEXT', 'RESULT', 'SCORE']
        data = pd.DataFrame(columns=cols)
        for i in range(len(csv)):
            apiURL = 'http://124.158.1.125:8807/sentiment?text=' + csv['TEXT'][i]
            f = requests.get(apiURL)
            f = f.json()
            print(f[0])
            new_data = pd.Series([csv.iloc[i]['TEXT'], f[0]['result'], f[0]['score']], index = data.columns)
            data = data.append(new_data, ignore_index=True)
            # tương tự, lưu mỗi time thui
        data.to_csv('./static/' + time_sub + '.csv', index=False, encoding='utf-8')
        time_sub=time_sub + '.csv'
        return render_template('index.html', data=None, text='', file=time_sub)

if __name__ == '__main__':
    app.run(debug=True)
