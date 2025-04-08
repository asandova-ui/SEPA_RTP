// Variables globales para almacenar actor actual
let currentActorId = null;
let currentActorRole = null;

/* =========== CREAR ACTOR =========== */
document.getElementById('createActorForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const actorName = document.getElementById('actorName').value;
  const actorRole = document.getElementById('actorRole').value;

  const data = { name: actorName, role: actorRole };

  fetch('http://127.0.0.1:5000/actors', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    const actorResponseDiv = document.getElementById('actorResponse');
    actorResponseDiv.style.display = 'block';
    actorResponseDiv.innerText = JSON.stringify(result, null, 2);

    if (!result.error) {
      // Guardar actor_id y role
      currentActorId = result.id;
      currentActorRole = result.role;
      document.getElementById('currentActorId').innerText = currentActorId;
      document.getElementById('currentActorRole').innerText = currentActorRole;

      // Mostrar la sección correspondiente
      mostrarSeccionPorRol(currentActorRole);
    }
  })
  .catch(err => {
    console.error(err);
    const actorResponseDiv = document.getElementById('actorResponse');
    actorResponseDiv.style.display = 'block';
    actorResponseDiv.innerText = 'Error al crear actor.';
  });
});

function mostrarSeccionPorRol(role) {
  // Ocultamos todas las secciones
  document.getElementById('beneficiaryActions').style.display = 'none';
  document.getElementById('pspBeneficiaryActions').style.display = 'none';
  document.getElementById('pspPayerActions').style.display = 'none';
  document.getElementById('payerActions').style.display = 'none';

  // Mostramos la que corresponda al rol
  if (role === 'beneficiary') {
    document.getElementById('beneficiaryActions').style.display = 'block';
  } else if (role === 'psp_beneficiary') {
    document.getElementById('pspBeneficiaryActions').style.display = 'block';
  } else if (role === 'psp_payer') {
    document.getElementById('pspPayerActions').style.display = 'block';
  } else if (role === 'payer') {
    document.getElementById('payerActions').style.display = 'block';
  }
}

/* =========== BENEFICIARY: Crear RTP =========== */
document.getElementById('createRTPForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const iban = document.getElementById('iban').value;
  const amount = parseFloat(document.getElementById('amount').value);

  // Incluimos actor_id en la petición
  const data = {
    actor_id: currentActorId,
    iban: iban,
    amount: amount
  };

  fetch('http://127.0.0.1:5000/rtp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    const respDiv = document.getElementById('createRTPResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => {
    console.error(err);
    const respDiv = document.getElementById('createRTPResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = 'Error al crear RTP.';
  });
});

/* =========== PSP BENEFICIARY: Validar RTP =========== */
document.getElementById('validateBeneficiaryForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const rtpId = document.getElementById('rtpIdValidateBene').value;

  const data = {
    actor_id: currentActorId
  };

  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/validate-beneficiary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    const respDiv = document.getElementById('validateBeneficiaryResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => {
    console.error(err);
    const respDiv = document.getElementById('validateBeneficiaryResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = 'Error en validación beneficiary.';
  });
});

/* =========== PSP BENEFICIARY: Enrutar RTP =========== */
document.getElementById('routeForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const rtpId = document.getElementById('rtpIdRoute').value;

  const data = {
    actor_id: currentActorId
  };

  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    const respDiv = document.getElementById('routeResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => {
    console.error(err);
    const respDiv = document.getElementById('routeResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = 'Error al enrutar RTP.';
  });
});

/* =========== PSP PAYER: Validar RTP =========== */
document.getElementById('validatePayerForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const rtpId = document.getElementById('rtpIdValidatePayer').value;

  const data = {
    actor_id: currentActorId
  };

  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/validate-payer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    const respDiv = document.getElementById('validatePayerResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => {
    console.error(err);
    const respDiv = document.getElementById('validatePayerResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = 'Error en validación payer.';
  });
});

/* =========== PAYER: Decidir (aceptar o rechazar) =========== */
document.getElementById('decisionForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const rtpId = document.getElementById('rtpIdDecision').value;
  const decisionValue = document.getElementById('decision').value;

  const data = {
    actor_id: currentActorId,
    decision: decisionValue
  };

  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    const respDiv = document.getElementById('decisionResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => {
    console.error(err);
    const respDiv = document.getElementById('decisionResponse');
    respDiv.style.display = 'block';
    respDiv.innerText = 'Error en decisión payer.';
  });
});

/* =========== MOSTRAR LOGS =========== */
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

/* =========== Ocultar secciones al cargar la página =========== */
window.addEventListener('load', () => {
  // Al iniciar, no tenemos actor seleccionado
  document.getElementById('currentActorId').innerText = '';
  document.getElementById('currentActorRole').innerText = '';
});
