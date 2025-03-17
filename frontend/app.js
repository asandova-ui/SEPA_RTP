document.getElementById('rtpForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    // Obtener valores del formulario
    const iban = document.getElementById('iban').value;
    const amount = parseFloat(document.getElementById('amount').value);

    // Crear el objeto que se enviará
    const data = { iban, amount };

    // Hacer la petición POST a /rtp
    fetch('http://127.0.0.1:5000/rtp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        // Mostrar la respuesta en la página
        document.getElementById('response').innerText = JSON.stringify(result, null, 2);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('response').innerText = 'Ocurrió un error';
    });
});

// Validar
document.getElementById('validateForm').addEventListener('submit', event => {
    event.preventDefault();
    const rtpId = document.getElementById('rtpIdValidate').value;
  
    fetch(`http://127.0.0.1:5000/rtp/${rtpId}/validate`, {
      method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById('validateResponse').innerText = JSON.stringify(data, null, 2);
    })
    .catch(err => {
      console.error(err);
      document.getElementById('validateResponse').innerText = 'Error en validación';
    });
  });
  
  // Actualizar
  document.getElementById('updateForm').addEventListener('submit', event => {
    event.preventDefault();
    const rtpId = document.getElementById('rtpIdUpdate').value;
    const newStatus = document.getElementById('newStatus').value;
  
    fetch(`http://127.0.0.1:5000/rtp/${rtpId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById('updateResponse').innerText = JSON.stringify(data, null, 2);
    })
    .catch(err => {
      console.error(err);
      document.getElementById('updateResponse').innerText = 'Error en actualización';
    });
  });

  document.getElementById('showLogs').addEventListener('click', () => {
    fetch('http://127.0.0.1:5000/logs')
      .then(response => response.json())
      .then(logs => {
        let output = '<ul>';
        logs.forEach(log => {
          output += `<li>ID Log: ${log.id} | RTP: ${log.rtp_id} | old: ${log.old_status} -> new: ${log.new_status} | ${log.timestamp}</li>`;
        });
        output += '</ul>';
        document.getElementById('logsResponse').innerHTML = output;
      })
      .catch(err => console.error(err));
  });
  