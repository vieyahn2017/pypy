phantom.outputEncoding="gbk"

var url = 'http://www.yoka.com/dna/125/412/index.html';

var ajaxUrl_local = 'D:/scrapy/single/jquery-1.7.2.js';
var ajaxUrl_web = 'http://code.jquery.com/jquery-1.9.1.min.js'

var page = require('webpage').create();
page.settings.userAgent = 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727)';
console.log('The default user agent is ' + page.settings.userAgent);


page.open(url, function (status) {
    if (status != 'success') {
        console.log('Unable to access the website');
    } else {
        // 加载jQuery
		//console.log('123--- success');
		//console.log(page.content);

        page.injectJs(ajaxUrl_local);
        //page.includeJs(ajaxUrl_web)
		var val = page.evaluate(function(){
			/*
			var t=[];	//一个json对象数组 作为返回值
			$('#pbox img').each(function(){
				//建一个json对象  从循环体取两个元素 建立为json对象的记录 this.alt; this.src;
				var i={};
				i.alt=$(this).attr('alt');
				i.src=$(this).attr('src');
				t.push(i);
			});
			return JSON.stringify(t);
			*/
			return  $('#pbox img').map(function(){return {"alt":$(this).attr('alt'),"src":$(this).attr('src')}});
			
        });
//      console.log(JSON.stringify(val[0]));
        console.log(val);	
     	for(i in val){
     		try{
    		 console.log(  'The get elememts: \t' + val[i].src + ' , ' + val[i].alt //10.21 代码还是有部分问题，不过能输出了，
  		              // JSON.stringify(val[i])    10.21
  		              );
  		              //val[0]是object，会把所有proto的输出，  10.21
  		        }catch(e){}
  	}
		//console.log(val.length);
        phantom.exit();
     }
});
//0428运行成功的，现在运行不了了，悲乎
//val[0]是object，会把所有proto的输出，