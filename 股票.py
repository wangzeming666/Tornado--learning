# coding utf-8
'''tornado basic

'''
import requests
from tornado.httpserver import HTTPServer
import tornado
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        r = requests.get('http://web.juhe.cn:8080/finance/stock/hs?gid=sh601009&key=9c42ba92f54a3470dc328408624fcf2e')
        # 这里取出json中各种股票信息
        # 写到HTML页面中
        result = r.json()['result'][0]
        data = result['data']
        dapandata = result['dapandata']
        gopicture = result['gopicture']
        self.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<div>
	<div>
		<table border="1" cellspacing="0" width="1500px">
			<tr>
				<th>股票编号</th>
				<th>涨跌百分比</th>
				<th>涨跌额</th>
				<th>股票名称</th>
				<th>今日开盘价</th>
				<th>昨日收盘价</th>
				<th>当前价格</th>
				<th>今日最高价</th>
				<th>今日最低价</th>
				<th>竞买价</th>
				<th>竞卖价</th>
				<th>成交量</th>
				<th>成交金额</th>
			</tr>

			<tr>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
			</tr>
		</table>
	</div>
	<br/>
	<br/>
	<br/>
	<br/>
	

	<div>
		<table border="1" cellspacing="0" width="1500px">
			<tr>
				<th>买一</th>
				<th>买一报价</th>
				<th>买二</th>
				<th>买二报价</th>
				<th>买三</th>
				<th>买三报价</th>
				<th>买四</th>
				<th>买四报价</th>
				<th>买五</th>
				<th>买五报价</th>
				<th>卖一</th>
				<th>卖一报价</th>
				<th>卖二</th>
				<th>卖二报价</th>
				<th>卖三</th>
				<th>卖三报价</th>
				<th>卖四</th>
				<th>卖四报价</th>
				<th>卖五</th>
				<th>卖五报价</th>
				<th>日期</th>
				<th>时间</th>
			</tr>

			<tr>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
			</tr>
		</table>
	</div>

        <br/>
        <br/>
        <br/>
        
	<div>
		<table border="1" cellspacing="0" width="500px">
			<tr>
				<th colspan="6">大盘数据</th>
			</tr>

			<tr>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
				<td>{}</td>
			</tr>
		</table>
	</div>
        <br/>
        <br/><br/><br/><br/><br/>
        <br/>
	<div>
		<img src="{}" width="1000px" height="500px">
	</div>
	<br/><br/><br/><br/><br/>
	<br/>
	<br/>
	
	<div>
		<img src="{}" width="1000px" height="500px">
	</div>
	<br/>
	<br/><br/><br/><br/><br/>
	<br/>

	<div>
		<img src="{}" width="1000px" height="500px">
	</div>
	<br/>
	<br/><br/><br/><br/><br/>
	<br/>
	

	<div>
		<img src="{}" width="1000px" height="500px">
	</div>

	<div>
		<hr>
	</div>




</div>
</body>
</html>""".format(data['gid'], data['increPer'], data['increase'], data['name'], data['todayStartPri'], data['yestodEndPri'], data['nowPri'], data['todayMax'], data['todayMin'], data['competitivePri'], data['reservePri'], data['traNumber'], data['traAmount'], data['buyOne'], data['buyOnePri'], data['buyTwo'], data['buyTwoPri'], data['buyThree'], data['buyThreePri'], data['buyFour'], data['buyFourPri'], data['buyFive'], data['buyFivePri'], data['sellOne'], data['sellOnePri'], data['sellTwo'], data['sellTwoPri'], data['sellThree'], data['sellThreePri'], data['sellFour'], data['sellFourPri'], data['sellFive'], data['sellFivePri'], data['date'], data['time'], dapandata["dot"], dapandata["name"], dapandata["nowPic"], dapandata["rate"], dapandata["traAmount"], dapandata["traNumber"],gopicture['minurl'],gopicture['dayurl'],gopicture['weekurl'],gopicture['monthurl']))
    def post(self, *args, **kwargs):
        key = '9c42ba92f54a3470dc328408624fcf2e'
        # 这里获取gid股票号码，然后传给请求地址
        # 取代下方路径写死
        gid = 'sh601009'
        r = requests.get('http://web.juhe.cn:8080/finance/stock/hs?gid=sh601009&key=9c42ba92f54a3470dc328408624fcf2e')
        # 这里取出json中各种股票信息
        # 写到HTML页面中
        result = r.json()['result'][0]
        data = result['data']
        dapandata = result['dapandata']
        gopicture = result['gopicture']
        self.write("""<<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<div>
	<div>
		<table>
			<tr>
				<th>股票编号</th>
				<th>涨跌百分比</th>
				<th>涨跌额</th>
				<th>股票名称</th>
				<th>今日开盘价</th>
				<th>昨日收盘价</th>
				<th>当前价格</th>
				<th>今日最高价</th>
				<th>今日最低价</th>
				<th>竞买价</th>
				<th>竞卖价</th>
				<th>成交量</th>
				<th>成交金额</th>
			</tr>

			<tr>
				<td>{}</td>
				<td>data['increPer']</td>
				<td>data['increase']</td>
				<td>data['name']</td>
				<td>data['todayStartPri']</td>
				<td>data['yestodEndPri']</td>
				<td>data['nowPri']</td>
				<td>data['todayMax']</td>
				<td>data['todayMin']</td>
				<td>data['competitivePri']</td>
				<td>data['reservePri']</td>
				<td>data['traNumber']</td>
				<td>data['traAmount']</td>
			</tr>
		</table>
	</div>

	<div>
		<table>
			<tr>
				<th>买一</th>
				<th>买一报价</th>
				<th>买二</th>
				<th>买二报价</th>
				<th>买三</th>
				<th>买三报价</th>
				<th>买四</th>
				<th>买四报价</th>
				<th>买五</th>
				<th>买五报价</th>
				<th>卖一</th>
				<th>卖一报价</th>
				<th>卖二</th>
				<th>卖二报价</th>
				<th>卖三</th>
				<th>卖三报价</th>
				<th>卖四</th>
				<th>卖四报价</th>
				<th>卖五</th>
				<th>卖五报价</th>
				<th>日期</th>
				<th>时间</th>
			</tr>

			<tr>
				<td>data['buyOne']</td>
				<td>data['buyOnePri']</td>
				<td>data['buyTwo']</td>
				<td>data['buyTwoPri']</td>
				<td>data['buyThree']</td>
				<td>data['buyThreePri']</td>
				<td>data['buyFour']</td>
				<td>data['buyFourPri']</td>
				<td>data['buyFive']</td>
				<td>data['buyFivePri']</td>
				<td>data['sellOne']</td>
				<td>data['sellOnePri']</td>
				<td>data['sellTwo']</td>
				<td>data['sellTwoPri']</td>
				<td>data['sellThree']</td>
				<td>data['sellThreePri']</td>
				<td>data['sellFour']</td>
				<td>data['sellFourPri']</td>
				<td>data['sellFive']</td>
				<td>data['sellFivePri']</td>
				<td>data['date']</td>
				<td>data['time']</td>
			</tr>
		</table>
	</div>

	<div>
		<table>
			<tr>
				<th colspan="6">大盘数据</th>
			</tr>

			<tr>
				<td>dapandata["dot"]</td>
				<td>dapandata["name"]</td>
				<td>dapandata["nowPic"]</td>
				<td>dapandata["rate"]</td>
				<td>dapandata["traAmount"]</td>
				<td>dapandata["traNumber"]</td>
			</tr>
		</table>
	</div>

	<div>
		<img src="gopicture['minurl']">
	</div>
	
	<div>
		<img src="gopicture['dayurl']">
	</div>	

	<div>
		<img src="gopicture['weekurl']">
	</div>

	<div>
		<img src="gopicture['monthly']">
	</div>

	<div>
		<hr>
	</div>




</div>
</body>
</html>""".format(data['gid']))
        

# create application instance
app = Application([
    ("/", IndexHandler),

])

server = HTTPServer(app)
server.listen(8888)
IOLoop.instance().start()
