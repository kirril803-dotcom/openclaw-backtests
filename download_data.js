// Download BTC data and save to CSV
const https = require('https');

const url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=500';

https.get(url, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        const klines = JSON.parse(data);
        const lines = ['datetime,open,high,low,close,volume'];
        klines.forEach(k => {
            const timestamp = Math.floor(k[0] / 1000);
            lines.push(`${timestamp},${k[1]},${k[2]},${k[3]},${k[4]},${k[5]}`);
        });
        const fs = require('fs');
        fs.writeFileSync('./data/btc_data.csv', lines.join('\n'));
        console.log('BTC data saved to data/btc_data.csv');
    });
}).on('error', console.error);
