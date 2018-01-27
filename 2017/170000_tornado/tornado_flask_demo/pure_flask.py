# -*- coding: utf-8 -*- 

from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def main_handler():
    # return render_template('main.html', messages="whatever",title="home")
    return 'You are welcome!'
    
if __name__ == '__main__':
    app.run(port=8888, debug=False)