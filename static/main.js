function fetchSensorData() {
    return fetch('/api/sensors')
        .then(function (response) {
            return response.json();
        })
        .then(function (payload) {
            return payload.data || [];
        })
        .catch(function (err) {
            console.error('Ошибка загрузки данных датчиков:', err);
            return [];
        });
}

function buildCharts(data) {
    var ctxTemp = document.getElementById('tempChart').getContext('2d');
    var ctxHum = document.getElementById('humChart').getContext('2d');

    var labels = data.map(function (item) {
        // Показываем только часы и минуты
        var d = new Date(item.timestamp);
        var hours = ('0' + d.getHours()).slice(2);
        var minutes = ('0' + d.getMinutes()).slice(2);
        return hours + ':' + minutes;
    });

    var temps = data.map(function (item) {
        return item.temperature;
    });

    var hums = data.map(function (item) {
        return item.humidity;
    });

    new Chart(ctxTemp, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Температура, °C',
                data: temps,
                borderColor: 'rgba(239, 68, 68, 1)',
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                pointRadius: 0,
                borderWidth: 2,
                lineTension: 0.25
            }]
        },
        options: {
            legend: {
                labels: {
                    fontColor: '#e5e7eb'
                }
            },
            scales: {
                xAxes: [{
                    ticks: {
                        fontColor: '#9ca3af',
                        maxTicksLimit: 12
                    },
                    gridLines: {
                        color: 'rgba(55,65,81,0.4)'
                    }
                }],
                yAxes: [{
                    ticks: {
                        fontColor: '#9ca3af'
                    },
                    gridLines: {
                        color: 'rgba(55,65,81,0.4)'
                    }
                }]
            }
        }
    });

    new Chart(ctxHum, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Влажность, %',
                data: hums,
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.15)',
                pointRadius: 0,
                borderWidth: 2,
                lineTension: 0.25
            }]
        },
        options: {
            legend: {
                labels: {
                    fontColor: '#e5e7eb'
                }
            },
            scales: {
                xAxes: [{
                    ticks: {
                        fontColor: '#9ca3af',
                        maxTicksLimit: 12
                    },
                    gridLines: {
                        color: 'rgba(55,65,81,0.4)'
                    }
                }],
                yAxes: [{
                    ticks: {
                        fontColor: '#9ca3af'
                    },
                    gridLines: {
                        color: 'rgba(55,65,81,0.4)'
                    }
                }]
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    fetchSensorData().then(function (data) {
        buildCharts(data);
    });
});

