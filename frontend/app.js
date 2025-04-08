// Variables globales
let currentActorId = null;
let currentActorRole = null;

/** 
 * crearActor:
 * Llama al endpoint /actors con un NOMBRE HARDCODED Y ROL dado por parámetro.
 * Se usará cuando pulsemos uno de los 4 botones de "Crear Actores".
 */
function crearActor(role) {
  // Podrías pedirle un nombre por prompt(), o generarlo aleatorio, etc.
  const defaultName = prompt(`Introduzca el nombre del actor para el rol ${role}:`, `${role}_name`);
  if (!defaultName) {
    return; // Usuario canceló
  }

  const data = { 
    name: defaultName,
    role: role
  };

  fetch('http://127.0.0.1:5000/actors', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
    const msgDiv = document.getElementById('actorCreationResponse');
    msgDiv.classList.remove('invisible-section');
    msgDiv.innerHTML = JSON.stringify(result, null, 2);
  })
  .catch(err => {
    console.error(err);
  });
}

// Manejar el formulario de "Seleccionar Actor Activo"
document.getElementById('selectActorForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const actorIdInput = document.getElementById('actorIdSelect');
  const actorIdValue = parseInt(actorIdInput.value);

  if (!actorIdValue) return;

  // Llamamos a un endpoint para verificar qué rol tiene
  // Si no existe actor, sale error
  // Sino, actualizamos currentActorId, currentActorRole
  fetch(`http://127.0.0.1:5000/actors_info/${actorIdValue}`, {
    method: 'GET'
  })
  .then(res => res.json())
  .then(data => {
    // Si hay error, lo mostramos
    if (data.error) {
      document.getElementById('selectActorError').classList.remove('invisible-section');
      document.getElementById('selectActorError').innerText = data.error;
      document.getElementById('currentActorCard').classList.add('invisible-section');
      return;
    }

    // Sino, asignamos actor actual
    currentActorId = data.id;
    currentActorRole = data.role;
    // Mostramos cartita
    document.getElementById('selectActorError').classList.add('invisible-section');
    document.getElementById('currentActorCard').classList.remove('invisible-section');
    document.getElementById('currentActorId').innerText = data.id;
    document.getElementById('currentActorRole').innerText = data.role;

    // Mostramos/ocultamos secciones en función del rol
    mostrarAccionesPorRol(data.role);
  })
  .catch(err => console.error(err));
});

/**
 * mostrarAccionesPorRol
 * Oculta todos los paneles de acciones y sólo muestra el que corresponde al rol actual.
 */
function mostrarAccionesPorRol(role) {
  // Ocultar todo
  document.getElementById('beneficiaryActions').classList.add('invisible-section');
  document.getElementById('pspBeneficiaryActions').classList.add('invisible-section');
  document.getElementById('pspPayerActions').classList.add('invisible-section');
  document.getElementById('payerActions').classList.add('invisible-section');

  if (role === 'beneficiary') {
    document.getElementById('beneficiaryActions').classList.remove('invisible-section');
  } else if (role === 'psp_beneficiary') {
    document.getElementById('pspBeneficiaryActions').classList.remove('invisible-section');
  } else if (role === 'psp_payer') {
    document.getElementById('pspPayerActions').classList.remove('invisible-section');
  } else if (role === 'payer') {
    document.getElementById('payerActions').classList.remove('invisible-section');
  }
}

/**
 * FORM: Crear RTP (Beneficiary)
 */
document.getElementById('createRTPForm').addEventListener('submit', function(e) {
  e.preventDefault();
  // Leemos campos
  const iban = document.getElementById('ibanField').value;
  const amount = parseFloat(document.getElementById('amountField').value);
  const pspBenef = parseInt(document.getElementById('pspBenefField').value);
  const pspPayer = parseInt(document.getElementById('pspPayerField').value);
  const payerId = parseInt(document.getElementById('payerField').value);

  // actor_id es el beneficiary actual
  const data = {
    actor_id: currentActorId,
    psp_beneficiary_id: pspBenef,
    psp_payer_id: pspPayer,
    payer_id: payerId,
    iban: iban,
    amount: amount
  };

  fetch('http://127.0.0.1:5000/rtp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
    const resp = document.getElementById('createRTPResponse');
    resp.classList.remove('invisible-section');
    resp.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => console.error(err));
});

/**
 * FORM: PSP Beneficiary -> Validar
 */
document.getElementById('validateBeneficiaryForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const rtpId = document.getElementById('rtpIdValidateBene').value;

  const data = {
    actor_id: currentActorId
  };
  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/validate-beneficiary`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
    const resp = document.getElementById('validateBeneficiaryResponse');
    resp.classList.remove('invisible-section');
    resp.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => console.error(err));
});

/**
 * FORM: PSP Beneficiary -> Enrutar
 */
document.getElementById('routeForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const rtpId = document.getElementById('rtpIdRoute').value;

  const data = {
    actor_id: currentActorId
  };
  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/route`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
    const resp = document.getElementById('routeResponse');
    resp.classList.remove('invisible-section');
    resp.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => console.error(err));
});

/**
 * FORM: PSP Payer -> Validar
 */
document.getElementById('validatePayerForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const rtpId = document.getElementById('rtpIdValidatePayer').value;

  const data = {
    actor_id: currentActorId
  };
  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/validate-payer`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
    const resp = document.getElementById('validatePayerResponse');
    resp.classList.remove('invisible-section');
    resp.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => console.error(err));
});

/**
 * FORM: Payer -> Decisión
 */
document.getElementById('decisionForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const rtpId = document.getElementById('rtpIdDecision').value;
  const decisionValue = document.getElementById('decision').value;

  const data = {
    actor_id: currentActorId,
    decision: decisionValue
  };
  fetch(`http://127.0.0.1:5000/rtp/${rtpId}/decision`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(result => {
    const resp = document.getElementById('decisionResponse');
    resp.classList.remove('invisible-section');
    resp.innerText = JSON.stringify(result, null, 2);
  })
  .catch(err => console.error(err));
});

/**
 * Botón: Mostrar Logs
 */
document.getElementById('showLogs').addEventListener('click', () => {
  fetch(`http://127.0.0.1:5000/logs`)
    .then(res => res.json())
    .then(logs => {
      let html = `<ul class="list-group">`;
      logs.forEach(log => {
        html += `<li class="list-group-item">
          <strong>LogID ${log.id} </strong> 
          [RTP ${log.rtp_id}] 
          ${log.old_status} => ${log.new_status} 
          <small>(${log.timestamp})</small>
          </li>`;
      });
      html += `</ul>`;

      document.getElementById('logsResponse').innerHTML = html;
    })
    .catch(err => console.error(err));
});

/**
 * Al arrancar la página, no hace nada especial,
 * pero podríamos ocultar secciones si fuera necesario.
 */

// Extra: Endpoint /actors_info/<id> para obtener info de un actor:
 // Deberás crear en tu backend la ruta GET /actors_info/<int:actor_id>
 // para que devuelva {id,role,...} o error si no existe.
