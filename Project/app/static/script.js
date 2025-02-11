// script.js

document.addEventListener("DOMContentLoaded", () => {
    const basurerosList = document.getElementById("basurero-items");
    const ID = document.getElementById("selected-id");
    const basureroDetail = document.getElementById("basurero-detail");
    const backButton = document.getElementById("back-button");
    const nivelUltrasonico = document.getElementById("nivel-ultrasonico");
    const pesoActual = document.getElementById("peso-actual");
    const basureroTitle = document.getElementById("basurero-title");
    const chartContainer = document.getElementById("chart-container");
    let basureroChart;
    //let path = 'http://192.168.1.66'
    let path = 'https://riobambalocal.com'
    

    // Simulated Data for Initial Setup (Replace with MQTT logic later)
    //const basureros = [
    //    { id: "1", nivel_ultrasonico: 30, peso_actual: 12 },
    //    { id: "2", nivel_ultrasonico: 50, peso_actual: 20 },
    //    { id: "3", nivel_ultrasonico: 10, peso_actual: 5 },
    //    { id: "4", nivel_ultrasonico: 40, peso_actual: 5 },
    //];

    function getBasureros() {
        //fetch( `${path}:8000/basureros`) // Cambia la URL según sea necesario
        fetch('/basureros') // Cambia la URL según sea necesario
            .then(response => response.json())
            .then(data => {
                loadBasureros(data);  // Pasamos los datos obtenidos a la función loadBasureros
                console.log(data)
            })
            
            .catch(error => {
                console.error('Error al obtener los basureros:', error);
            });
    }


    
    // Load Basureros into the List
    function loadBasureros(basureros) {
        console.log(`los basureros: ${basureros}`)
        basurerosList.innerHTML = "";

        basureros.forEach((basurero) => {
            const li = document.createElement("li");
            li.textContent = `Basurero ID: ${basurero}`;
            li.addEventListener("click", () => showBasureroDetail(basurero));
            basurerosList.appendChild(li);
        });
    }
    
    getBasureros()
    
    function showBasureroDetail(basureroId) {
        fetch(`/basureros/${basureroId}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Ocultar la lista de basureros y mostrar los detalles
            basurerosList.parentElement.style.display = "none";
            basureroDetail.classList.remove("hidden");
            basureroTitle.textContent = `Detalles del Basurero ${basureroId}`;
            
            // Mostrar solo la última medición en los detalles
            if (data.length > 0) {
                const lastMeasurement = data[0];  // La última medición es la primera (última en la DB)
                ID.textContent = `${basureroId}`;
                nivelUltrasonico.textContent = `${lastMeasurement.nivel_ultrasonico}%`;
                pesoActual.textContent = `${lastMeasurement.peso_actual}`;
            }
            getLocation()
            
            // Actualizar la gráfica con las últimas 10 mediciones (si hay más de 10)
            const last10Measurements = data.slice(0, 10);  // Solo las primeras 10 mediciones
            console.log(last10Measurements)
            updateChart(last10Measurements);

                
                
            })
            .catch(error => {
                console.error('Error al obtener los detalles del basurero:', error);
            });
    }



    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(sendLocation, showError);
        } else {
            alert("La geolocalización no es soportada por este navegador.");
        }
    }
    
    function sendLocation(position) {
        const data = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
        };
        console.log(`la ubicacion detectada es: ${data.longitude}, ${data.latitude}`)

        fetch(`${path}/get_location/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(() => {
            // Una vez que la solicitud se complete y el mapa sea generado, actualizamos el iframe
            const iframe = document.getElementById("map-iframe");
            iframe.src = "/static/ruta_map.html";  // Actualizamos el src con el archivo del mapa generado
            iframe.style.display = "block";  // Mostramos el iframe
        })
        .catch(error => console.error('Error al generar el mapa:', error));
        //.then(data => calculateRoute(data.latitude, data.longitude))
        //.catch(error => console.error('Error:', error));
    }

    function calculateRoute(lat, lon) {
        fetch('/calculate_route/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lon })
        })
        .then(response => response.json())
        .then(data => alert(`Ruta Calculada: ${JSON.stringify(data.path)}`))
        .catch(error => console.error('Error:', error));
    }

    function showError(error) {
        alert("Error al obtener ubicación: " + error.message);
    }
    


    // Show Details of Selected Basurero
    //function showBasureroDetail(basureroId) {
    //    fetch(`http://127.0.0.1:8000/basureros/${basureroId}`)
    //        .then(response => response.json())
    //        .then(data => {
    //            console.log(data)
    //            basurerosList.parentElement.style.display = "none";
    //            basureroDetail.classList.remove("hidden");
    //            basureroTitle.textContent = `Detalles del Basurero ${data.id}`;
    //            nivelUltrasonico.textContent = `${data.nivel_ultrasonico}%`;
    //            pesoActual.textContent = `${data.peso_actual}`;
    //            updateChart(data);
    //            // Limpiar detalles anteriores
    //            //basureroDetail.innerHTML = `<h3>Detalles del Basurero ID: ${basureroId}</h3>`;
    //            //
    //            //// Mostrar los detalles del basurero
    //            //data.forEach(item => {
    //            //    const p = document.createElement("p");
    //            //    p.textContent = `Nivel Ultrasonico: ${item.nivel_ultrasonico}, Peso Actual: ${item.peso_actual}, Timestamp: ${item.timestamp}`;
    //            //    basureroDetail.appendChild(p);
    //            //});
    //        })
    //        .catch(error => {
    //            console.error('Error al obtener los detalles del basurero:', error);
    //        });
    //}

    //function showBasureroDetail(basurero) {
    //    basurerosList.parentElement.style.display = "none";
    //    basureroDetail.classList.remove("hidden");
    //    basureroTitle.textContent = `Detalles del Basurero ${basurero.id}`;
    //    nivelUltrasonico.textContent = `${basurero.nivel_ultrasonico}%`;
    //    pesoActual.textContent = `${basurero.peso_actual}`;
    //    updateChart(basurero);
    //}

    // Back to List View
    backButton.addEventListener("click", () => {
        basurerosList.parentElement.style.display = "block";
        basureroDetail.classList.add("hidden");
    });

    // Update Chart with Data
    function updateChart(basurero) {
        if (basureroChart) {
            basureroChart.destroy();
        }   
    
        const ctx = document.createElement("canvas");
        chartContainer.innerHTML = "";  // Limpiar el contenedor anterior
        chartContainer.appendChild(ctx);
    
        // Preparar los datos para la gráfica
        const timestamps = basurero.map(item => item.timestamp); // Extraer los timestamps
        const nivelesUltrasonico = basurero.map(item => item.nivel_ultrasonico); // Extraer niveles ultrasonicos
    
        basureroChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: timestamps, // Usamos los timestamps como etiquetas del eje X
                datasets: [
                    {
                        label: "Nivel Ultrasonico (%)",
                        data: nivelesUltrasonico, // Usamos los valores reales de nivel ultrasonico
                        borderColor: "#007BFF",
                        backgroundColor: "rgba(0, 123, 255, 0.2)",
                        tension: 0.4,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "top",
                    },
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Timestamp", // Titulo para el eje X
                        },
                        ticks: {
                            autoSkip: true, // Para evitar que los timestamps se solapen
                            maxTicksLimit: 10, // Limitar la cantidad de marcas en el eje X
                        },
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Nivel Ultrasonico (%)", // Titulo para el eje Y
                        },
                    },
                },
            },
        });
    }
    

    //function updateChart(basurero) {
    //    if (basureroChart) {
    //        basureroChart.destroy();
    //    }
//
    //    const ctx = document.createElement("canvas");
    //    chartContainer.innerHTML = "";
    //    chartContainer.appendChild(ctx);
//
    //    basureroChart = new Chart(ctx, {
    //        type: "line",
    //        data: {
    //            labels: ["T1", "T2", "T3", "T4", "T5"], // Replace with timestamps
    //            datasets: [
    //                {
    //                    label: "Nivel Ultrasonico (%)",
    //                    data: [
    //                        basurero.nivel_ultrasonico,
    //                        basurero.nivel_ultrasonico - 5,
    //                        basurero.nivel_ultrasonico - 10,
    //                        basurero.nivel_ultrasonico - 15,
    //                        basurero.nivel_ultrasonico - 20,
    //                    ], // Replace with actual historical data
    //                    borderColor: "#007BFF",
    //                    backgroundColor: "rgba(0, 123, 255, 0.2)",
    //                    tension: 0.4,
    //                },
    //            ],
    //        },
    //        options: {
    //            responsive: true,
    //            plugins: {
    //                legend: {
    //                    position: "top",
    //                },
    //            },
    //        },
    //    });
    //}

    //loadBasureros();

    // Placeholder for MQTT Connection Logic
    // Here, you will integrate MQTT.js or similar library to subscribe to your broker and fetch real-time data.
});
