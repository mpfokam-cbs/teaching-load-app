const API = "/api";
const TYPES_GROUPE_UNIQUE = ["TD", "TP", "TPE"]; // un groupe = un seul enseignant

/* ---------- Aide générique pour appeler l'API ---------- */
async function api(method, url, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(API + url, opts);
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error((data && data.error) || "Erreur inconnue");
  return data;
}

/* ---------- Notifications (corrige l'absence de retour visuel) ---------- */
let toastTimer = null;
function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = "toast show" + (isError ? " error" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.className = "toast"; }, 4000);
}

/* ---------- Onglets (implémentation maison, sans dépendance) ---------- */
function initTabs() {
  const buttons = document.querySelectorAll(".tab-btn");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetSelector = btn.getAttribute("data-bs-target");
      buttons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.querySelector(targetSelector).classList.add("active");

      if (targetSelector === "#dashboard") loadDashboard();
      if (targetSelector === "#interventions") loadInterventions();
      if (targetSelector === "#recapitulatif") loadRecapitulatif();
    });
  });
}

/* ---------- Modales (implémentation maison) ---------- */
function openModal(id) {
  document.getElementById(id).classList.add("open");
}
function closeModal(id) {
  document.getElementById(id).classList.remove("open");
}
document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
  backdrop.addEventListener("click", e => {
    if (e.target === backdrop) backdrop.classList.remove("open");
  });
});

/* ---------- État local ---------- */
let formations = [];
let ues = [];
let enseignants = [];

/* ===================== FORMATIONS ===================== */
async function loadFormations() {
  formations = await api("GET", "/formations");
  renderFormations();
  fillFormationSelects();
}

function renderFormations() {
  const tbody = document.querySelector("#table-formations tbody");
  tbody.innerHTML = "";
  formations.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${f.id}</td><td>${f.faculte}</td><td>${f.departement}</td>
      <td>${f.filiere}</td><td>${f.niveau}</td><td>${f.annee_academique}</td>
      <td><button class="btn-sm danger" data-id="${f.id}">Supprimer</button></td>`;
    tr.querySelector("button").addEventListener("click", () => deleteFormation(f.id));
    tbody.appendChild(tr);
  });
}

function fillFormationSelects() {
  document.querySelectorAll(".select-formation").forEach(sel => {
    sel.innerHTML = formations
      .map(f => `<option value="${f.id}">${f.filiere} (${f.niveau}) — ${f.annee_academique}</option>`)
      .join("");
  });
}

document.getElementById("form-formation").addEventListener("submit", async e => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  try {
    await api("POST", "/formations", data);
    e.target.reset();
    showToast("Formation enregistrée.");
    await loadFormations();
  } catch (err) { showToast(err.message, true); }
});

async function deleteFormation(id) {
  if (!confirm("Supprimer cette formation et toutes ses UE ?")) return;
  await api("DELETE", `/formations/${id}`);
  showToast("Formation supprimée.");
  await loadFormations();
  await loadUEs();
}

/* ===================== UE ===================== */
async function loadUEs() {
  ues = await api("GET", "/ues");
  renderUEs();
  fillUESelects();
}

function renderUEs() {
  const tbody = document.querySelector("#table-ues tbody");
  tbody.innerHTML = "";
  ues.forEach(u => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${u.id}</td><td>${u.code}</td><td>${u.intitule}</td><td>${u.effectif_etudiant}</td>
      <td>${u.volume_cm}h / cap. ${u.capacite_cm}</td>
      <td>${u.volume_td}h / cap. ${u.capacite_td}</td>
      <td>${u.volume_tp}h / cap. ${u.capacite_tp}</td>
      <td>${u.volume_tpe}h / cap. ${u.capacite_tpe}</td>
      <td>
        <button class="btn-sm outline" data-action="charge">Charge</button>
        <button class="btn-sm" data-action="edit">Modifier</button>
        <button class="btn-sm danger" data-action="del">Supprimer</button>
      </td>`;
    tr.querySelector('[data-action="charge"]').addEventListener("click", () => voirChargeUE(u.id));
    tr.querySelector('[data-action="edit"]').addEventListener("click", () => editUE(u.id));
    tr.querySelector('[data-action="del"]').addEventListener("click", () => deleteUE(u.id));
    tbody.appendChild(tr);
  });
}

function fillUESelects() {
  document.querySelectorAll(".select-ue").forEach(sel => {
    const previous = sel.value;
    sel.innerHTML = ues.map(u => `<option value="${u.id}">${u.code} — ${u.intitule}</option>`).join("");
    if (previous && ues.some(u => String(u.id) === previous)) sel.value = previous;
  });
  const filtre = document.getElementById("filtre-ue-interventions");
  filtre.innerHTML = `<option value="">Toutes les UE</option>` +
    ues.map(u => `<option value="${u.id}">${u.code} — ${u.intitule}</option>`).join("");
}

function editUE(id) {
  const u = ues.find(x => x.id === id);
  if (!u) return;
  const form = document.getElementById("form-ue");
  form.formation_id.value = u.formation_id;
  form.code.value = u.code;
  form.intitule.value = u.intitule;
  form.semestre.value = u.semestre;
  form.credits.value = u.credits;
  form.effectif_etudiant.value = u.effectif_etudiant;
  form.volume_cm.value = u.volume_cm;
  form.volume_td.value = u.volume_td;
  form.volume_tp.value = u.volume_tp;
  form.volume_tpe.value = u.volume_tpe;
  form.capacite_cm.value = u.capacite_cm;
  form.capacite_td.value = u.capacite_td;
  form.capacite_tp.value = u.capacite_tp;
  form.capacite_tpe.value = u.capacite_tpe;

  document.getElementById("ue-edit-id").value = u.id;
  document.getElementById("ue-form-title").textContent = `Modifier l'UE — ${u.code}`;
  document.getElementById("ue-submit-btn").textContent = "Enregistrer les modifications";
  document.getElementById("ue-cancel-edit").style.display = "inline-block";
  document.getElementById("ues").scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetUEForm() {
  document.getElementById("form-ue").reset();
  document.getElementById("ue-edit-id").value = "";
  document.getElementById("ue-form-title").textContent = "Nouvelle unité d'enseignement";
  document.getElementById("ue-submit-btn").textContent = "Enregistrer l'UE";
  document.getElementById("ue-cancel-edit").style.display = "none";
}

document.getElementById("ue-cancel-edit").addEventListener("click", resetUEForm);

document.getElementById("form-ue").addEventListener("submit", async e => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  ["formation_id", "credits", "effectif_etudiant", "capacite_cm", "capacite_td", "capacite_tp", "capacite_tpe"]
    .forEach(k => data[k] = parseInt(data[k] || 0, 10));
  ["volume_cm", "volume_td", "volume_tp", "volume_tpe"].forEach(k => data[k] = parseFloat(data[k] || 0));
  const editId = document.getElementById("ue-edit-id").value;
  try {
    if (editId) {
      await api("PUT", `/ues/${editId}`, data);
      showToast("UE modifiée avec succès.");
    } else {
      await api("POST", "/ues", data);
      showToast("UE enregistrée avec succès.");
    }
    resetUEForm();
    await loadUEs();
    await loadInterventions();
  } catch (err) { showToast(err.message, true); }
});

async function deleteUE(id) {
  if (!confirm("Supprimer cette UE et ses répartitions associées ?")) return;
  await api("DELETE", `/ues/${id}`);
  showToast("UE supprimée.");
  await loadUEs();
  await loadInterventions();
}

async function voirChargeUE(id) {
  const etat = await api("GET", `/ues/${id}/etat`);
  const ue = ues.find(u => u.id === id);

  let html = `<h5>${ue.code} — ${ue.intitule}</h5>`;
  html += `<table><thead><tr><th>Type</th><th>Groupes</th><th>Heures / groupe</th><th>Charge</th><th>Répartition</th></tr></thead><tbody>`;

  ["CM", "TD", "TP", "TPE"].forEach(t => {
    const info = etat[t];
    let repartition;
    if (t === "CM") {
      const attributions = info.groupes.flatMap(g => g.attributions);
      repartition = attributions.length
        ? attributions.map(a => `${nomEnseignant(a.enseignant_id)} (${a.heures} h)`).join(", ")
        : "<em>aucune attribution</em>";
      const restant = info.groupes.reduce((s, g) => s + g.heures_restantes, 0);
      if (restant > 0) repartition += ` — <span class="text-warn">${restant} h non attribuées</span>`;
    } else {
      const occupes = info.groupes.filter(g => !g.libre).length;
      repartition = `${occupes} / ${info.nombre_groupes} groupe(s) attribué(s)`;
    }
    html += `<tr><td>${t}</td><td>${info.nombre_groupes}</td><td>${info.heures_par_groupe} h</td>
      <td>${(info.nombre_groupes * info.heures_par_groupe)} h</td><td>${repartition}</td></tr>`;
  });
  html += `<tr class="total"><td colspan="3">Total</td><td colspan="2">${etat.total} h</td></tr>`;
  html += `</tbody></table>`;

  document.getElementById("ue-charge-result").innerHTML = html;
  openModal("modal-ue-charge");
}

function nomEnseignant(id) {
  const e = enseignants.find(x => x.id === id);
  return e ? `${e.prenom} ${e.nom}` : `#${id}`;
}

/* ===================== ENSEIGNANTS ===================== */
async function loadEnseignants() {
  enseignants = await api("GET", "/enseignants");
  renderEnseignants();
  fillEnseignantSelects();
}

function renderEnseignants() {
  const tbody = document.querySelector("#table-enseignants tbody");
  tbody.innerHTML = "";
  enseignants.forEach(e => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${e.id}</td><td>${e.prenom} ${e.nom}</td><td>${e.grade || "—"}</td><td>${e.departement || "—"}</td>
      <td>${e.volume_horaire_reference} h</td>
      <td>
        <button class="btn-sm outline" data-action="charge">Charge</button>
        <button class="btn-sm" data-action="edit">Modifier</button>
        <button class="btn-sm danger" data-action="del">Supprimer</button>
      </td>`;
    tr.querySelector('[data-action="charge"]').addEventListener("click", () => voirChargeEnseignant(e.id));
    tr.querySelector('[data-action="edit"]').addEventListener("click", () => editEnseignant(e.id));
    tr.querySelector('[data-action="del"]').addEventListener("click", () => deleteEnseignant(e.id));
    tbody.appendChild(tr);
  });
}

function fillEnseignantSelects() {
  document.querySelectorAll(".select-enseignant").forEach(sel => {
    sel.innerHTML = enseignants.map(e => `<option value="${e.id}">${e.prenom} ${e.nom}</option>`).join("");
  });
}

function editEnseignant(id) {
  const e = enseignants.find(x => x.id === id);
  if (!e) return;
  const form = document.getElementById("form-enseignant");
  form.nom.value = e.nom;
  form.prenom.value = e.prenom;
  form.grade.value = e.grade || "";
  form.departement.value = e.departement || "";
  form.specialite.value = e.specialite || "";
  form.volume_horaire_reference.value = e.volume_horaire_reference;

  document.getElementById("enseignant-edit-id").value = e.id;
  document.getElementById("enseignant-form-title").textContent = `Modifier — ${e.prenom} ${e.nom}`;
  document.getElementById("enseignant-submit-btn").textContent = "Enregistrer les modifications";
  document.getElementById("enseignant-cancel-edit").style.display = "inline-block";
  document.getElementById("enseignants").scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetEnseignantForm() {
  document.getElementById("form-enseignant").reset();
  document.getElementById("enseignant-edit-id").value = "";
  document.getElementById("enseignant-form-title").textContent = "Nouvel enseignant";
  document.getElementById("enseignant-submit-btn").textContent = "Enregistrer l'enseignant";
  document.getElementById("enseignant-cancel-edit").style.display = "none";
}

document.getElementById("enseignant-cancel-edit").addEventListener("click", resetEnseignantForm);

document.getElementById("form-enseignant").addEventListener("submit", async e => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  data.volume_horaire_reference = parseFloat(data.volume_horaire_reference || 192);
  const editId = document.getElementById("enseignant-edit-id").value;
  try {
    if (editId) {
      await api("PUT", `/enseignants/${editId}`, data);
      showToast("Enseignant modifié avec succès.");
    } else {
      await api("POST", "/enseignants", data);
      showToast("Enseignant enregistré avec succès.");
    }
    resetEnseignantForm();
    await loadEnseignants();
    await loadInterventions();
  } catch (err) { showToast(err.message, true); }
});

async function deleteEnseignant(id) {
  if (!confirm("Supprimer cet enseignant ?")) return;
  await api("DELETE", `/enseignants/${id}`);
  showToast("Enseignant supprimé.");
  await loadEnseignants();
  await loadInterventions();
}

async function voirChargeEnseignant(id) {
  const result = await api("GET", `/enseignants/${id}/charge`);
  let html = `<h5>${result.enseignant.prenom} ${result.enseignant.nom}</h5>`;
  html += `<table><thead><tr><th>UE</th><th>Type</th><th>Groupe n°</th><th>Heures</th></tr></thead><tbody>`;
  result.detail.forEach(d => {
    html += `<tr><td>${d.ue_code} — ${d.ue_intitule}</td><td>${d.type_enseignement}</td>
      <td>${d.groupe_numero}</td><td>${d.heures} h</td></tr>`;
  });
  html += `<tr class="total"><td colspan="3">Charge prévisionnelle</td><td>${result.charge_previsionnelle} h</td></tr>`;
  html += `</tbody></table>`;
  html += `<p class="hint">Total heure dû : ${result.charge_reference} h — Heure(s) complémentaire(s) : ${formatEcart(result.ecart)} h (${statutLabel(result.statut)})</p>`;
  document.getElementById("enseignant-charge-result").innerHTML = html;
  openModal("modal-enseignant-charge");
}

/* ===================== INTERVENTIONS ===================== */
async function loadInterventions() {
  const ueId = document.getElementById("filtre-ue-interventions").value;
  const items = await api("GET", `/interventions${ueId ? "?ue_id=" + ueId : ""}`);
  const tbody = document.querySelector("#table-interventions tbody");
  tbody.innerHTML = "";
  items.forEach(i => {
    const ue = ues.find(u => u.id === i.ue_id);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${ue ? ue.code : i.ue_id}</td>
      <td>${nomEnseignant(i.enseignant_id)}</td>
      <td>${i.type_enseignement}</td>
      <td>${i.groupe_numero}</td>
      <td>${i.type_enseignement === "CM" ? (i.heures + " h") : "groupe complet"}</td>
      <td><button class="btn-sm danger" data-action="del">Retirer</button></td>`;
    tr.querySelector('[data-action="del"]').addEventListener("click", () => deleteIntervention(i.id));
    tbody.appendChild(tr);
  });
  await updateGroupeOptions();
}

async function updateGroupeOptions() {
  const ueId = document.getElementById("intervention-ue").value;
  const type = document.getElementById("intervention-type").value;
  const hint = document.getElementById("intervention-hint");
  const isMulti = TYPES_GROUPE_UNIQUE.includes(type);

  document.getElementById("wrapper-groupe-cm").style.display = isMulti ? "none" : "block";
  document.getElementById("wrapper-groupe-multi").style.display = isMulti ? "block" : "none";

  if (!ueId) return;

  const disponibilite = await api("GET", `/ues/${ueId}/disponibilite?type=${type}`);

  if (disponibilite.nombre_groupes === 0) {
    document.getElementById("intervention-groupe-cm").innerHTML = "";
    document.getElementById("intervention-groupes-checkboxes").innerHTML = "";
    hint.textContent = "Aucun groupe n'est nécessaire pour cette UE (effectif nul).";
    return;
  }

  if (!isMulti) {
    // CM : un seul groupe sélectionnable à la fois, avec partage d'heures
    const groupeSelect = document.getElementById("intervention-groupe-cm");
    groupeSelect.innerHTML = disponibilite.groupes
      .map(g => `<option value="${g.groupe_numero}" data-restant="${g.heures_restantes}">
        Groupe n°${g.groupe_numero} — ${g.heures_restantes} h restantes sur ${g.heures_totales} h
      </option>`).join("");
    hint.textContent = "Le CM se partage entre plusieurs enseignants : indiquez la part d'heures prise par celui-ci.";
    updateHeuresMax();
  } else {
    // TD / TP / TPE : plusieurs groupes cochables, chacun réservé à un seul enseignant
    const libres = disponibilite.groupes.filter(g => g.libre);
    const container = document.getElementById("intervention-groupes-checkboxes");
    if (libres.length === 0) {
      container.innerHTML = `<p class="hint">Tous les groupes de ${type} de cette UE sont déjà attribués.</p>`;
      hint.textContent = "";
    } else {
      container.innerHTML = libres.map(g => `
        <label class="checkbox-item">
          <input type="checkbox" value="${g.groupe_numero}"> Groupe n°${g.groupe_numero} (${g.heures_totales} h)
        </label>`).join("");
      hint.textContent = `${libres.length} groupe(s) de ${type} encore disponible(s) sur ${disponibilite.nombre_groupes}.`;
    }
  }
}

function updateHeuresMax() {
  const type = document.getElementById("intervention-type").value;
  if (TYPES_GROUPE_UNIQUE.includes(type)) return;
  const groupeSelect = document.getElementById("intervention-groupe-cm");
  const selected = groupeSelect.selectedOptions[0];
  const heuresInput = document.getElementById("intervention-heures");
  if (selected) {
    heuresInput.max = selected.dataset.restant;
    heuresInput.placeholder = `max ${selected.dataset.restant} h`;
  }
}

document.getElementById("intervention-ue").addEventListener("change", updateGroupeOptions);
document.getElementById("intervention-type").addEventListener("change", updateGroupeOptions);
document.getElementById("intervention-groupe-cm").addEventListener("change", updateHeuresMax);

document.getElementById("form-intervention").addEventListener("submit", async e => {
  e.preventDefault();
  const ueId = parseInt(document.getElementById("intervention-ue").value, 10);
  const enseignantId = parseInt(document.querySelector('#form-intervention .select-enseignant').value, 10);
  const type = document.getElementById("intervention-type").value;

  if (!TYPES_GROUPE_UNIQUE.includes(type)) {
    // CM : une seule affectation, avec heures
    const groupeSelect = document.getElementById("intervention-groupe-cm");
    const groupeNumero = parseInt(groupeSelect.value, 10);
    const heures = parseFloat(document.getElementById("intervention-heures").value);
    if (!groupeNumero || !heures) { showToast("Veuillez indiquer un groupe et un nombre d'heures.", true); return; }
    try {
      await api("POST", "/interventions", {
        ue_id: ueId, enseignant_id: enseignantId, type_enseignement: type,
        groupe_numero: groupeNumero, heures,
      });
      showToast(`Enseignant affecté au CM (${heures} h) avec succès.`);
      await loadInterventions();
    } catch (err) { showToast(err.message, true); }
    return;
  }

  // TD / TP / TPE : une ou plusieurs cases cochées
  const cases = Array.from(document.querySelectorAll("#intervention-groupes-checkboxes input:checked"));
  if (cases.length === 0) {
    showToast("Veuillez cocher au moins un groupe à affecter.", true);
    return;
  }

  let succes = 0;
  const erreurs = [];
  for (const c of cases) {
    try {
      await api("POST", "/interventions", {
        ue_id: ueId, enseignant_id: enseignantId, type_enseignement: type,
        groupe_numero: parseInt(c.value, 10),
      });
      succes++;
    } catch (err) {
      erreurs.push(`Groupe n°${c.value} : ${err.message}`);
    }
  }

  if (succes > 0 && erreurs.length === 0) {
    showToast(`${succes} groupe(s) de ${type} affecté(s) avec succès.`);
  } else if (succes > 0 && erreurs.length > 0) {
    showToast(`${succes} groupe(s) affecté(s), ${erreurs.length} échec(s) : ${erreurs.join(" / ")}`, true);
  } else {
    showToast(`Aucune affectation réalisée : ${erreurs.join(" / ")}`, true);
  }
  await loadInterventions();
});

async function deleteIntervention(id) {
  await api("DELETE", `/interventions/${id}`);
  showToast("Affectation retirée.");
  await loadInterventions();
}

/* ===================== LIBELLÉS DE STATUT ===================== */
function statutLabel(statut) {
  if (statut === "equilibre") return "charge équilibrée";
  if (statut === "surcharge") return "surcharge prévisionnelle";
  return "charge inférieure au total dû";
}

function statutBadgeClass(statut) {
  if (statut === "equilibre") return "badge-equilibre";
  if (statut === "surcharge") return "badge-surcharge";
  return "badge-inferieur";
}

function formatEcart(ecart) {
  return (ecart > 0 ? "+" : "") + ecart;
}

/* ===================== TABLEAU DE BORD (détail par UE) ===================== */
async function loadDashboard() {
  const data = await api("GET", "/dashboard");
  const container = document.getElementById("dashboard-content");

  if (data.length === 0) {
    container.innerHTML = `<p class="hint">Aucun enseignant enregistré pour le moment.</p>`;
    return;
  }

  container.innerHTML = data.map(bloc => {
    const e = bloc.enseignant;
    let html = `<div class="enseignant-bloc">`;
    html += `<h3>${e.prenom} ${e.nom} <span class="muted">${e.grade ? "— " + e.grade : ""}</span></h3>`;

    if (bloc.lignes.length === 0) {
      html += `<p class="hint">Aucune intervention affectée pour le moment.</p>`;
    } else {
      html += `<table><thead><tr>
        <th>UE</th><th>CM (h)</th><th>TD (groupes / h)</th><th>TP (groupes / h)</th><th>TPE (groupes / h)</th><th>Total d'heure par UE</th>
      </tr></thead><tbody>`;
      bloc.lignes.forEach(l => {
        html += `<tr>
          <td>${l.ue_code} — ${l.ue_intitule}</td>
          <td>${l.cm_heures} h</td>
          <td>${l.td_groupes} / ${l.td_heures} h</td>
          <td>${l.tp_groupes} / ${l.tp_heures} h</td>
          <td>${l.tpe_groupes} / ${l.tpe_heures} h</td>
          <td>${l.total_ue} h</td>
        </tr>`;
      });
      html += `<tr class="total"><td colspan="5">Total heure par enseignant</td><td>${bloc.total_general} h</td></tr>`;
      html += `</tbody></table>`;
      html += `<p class="hint">Total heure dû : ${bloc.charge_reference} h — Heure(s) complémentaire(s) : ${formatEcart(bloc.ecart)} h —
        <span class="badge ${statutBadgeClass(bloc.statut)}">${statutLabel(bloc.statut)}</span></p>`;
    }
    html += `</div>`;
    return html;
  }).join("");
}

/* ===================== RÉCAPITULATIF ===================== */
async function loadSemestresFiltre() {
  const semestres = await api("GET", "/ues/semestres");
  const sel = document.getElementById("filtre-semestre");
  const previous = sel.value;
  sel.innerHTML = `<option value="">Année complète (tous semestres)</option>` +
    semestres.map(s => `<option value="${s}">${s}</option>`).join("");
  if (previous && semestres.includes(previous)) sel.value = previous;
}

async function loadRecapitulatif() {
  await loadSemestresFiltre();
  const semestre = document.getElementById("filtre-semestre").value;
  const data = await api("GET", `/recapitulatif${semestre ? "?semestre=" + encodeURIComponent(semestre) : ""}`);
  const tbody = document.querySelector("#table-recapitulatif tbody");
  tbody.innerHTML = "";
  data.forEach(d => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${d.enseignant.prenom} ${d.enseignant.nom}</td>
      <td>${d.charge_previsionnelle} h</td>
      <td>${d.charge_reference} h</td>
      <td>${formatEcart(d.ecart)} h</td>
      <td><span class="badge ${statutBadgeClass(d.statut)}">${statutLabel(d.statut)}</span></td>`;
    tbody.appendChild(tr);
  });
}

/* ===================== SIMULATION ===================== */
document.getElementById("form-simulation").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const data = { ue_id: parseInt(fd.get("ue_id"), 10), nouvel_effectif: parseInt(fd.get("nouvel_effectif"), 10) };
  try {
    const result = await api("POST", "/simulation", data);
    let html = `<p class="hint">Effectif : ${result.effectif_initial} → ${result.nouvel_effectif} étudiants</p>`;
    html += `<table><thead><tr><th>Type</th><th>Nouveaux groupes</th><th>Charge</th></tr></thead><tbody>`;
    ["CM", "TD", "TP", "TPE"].forEach(t => {
      html += `<tr><td>${t}</td><td>${result.nouveaux_groupes[t]}</td><td>${result.nouvelle_charge_ue[t].charge} h</td></tr>`;
    });
    html += `<tr class="total"><td colspan="2">Total d'heure par UE</td><td>${result.charge_totale_ue} h</td></tr></tbody></table>`;

    html += `<h5 style="margin-top:1.25rem;">Enseignants déjà affectés à cette UE</h5>`;
    if (result.enseignants_impactes.length === 0) {
      html += `<p class="hint">Aucun enseignant n'est encore affecté à cette UE.</p>`;
    } else {
      html += `<table><thead><tr><th>Enseignant</th><th>Charge (interventions déjà attribuées)</th><th>Total heure dû</th><th>Heure(s) complémentaire(s)</th></tr></thead><tbody>`;
      result.enseignants_impactes.forEach(en => {
        html += `<tr><td>${en.nom_complet}</td><td>${en.nouvelle_charge_previsionnelle} h</td>
          <td>${en.charge_reference} h</td><td>${formatEcart(en.ecart)} h</td></tr>`;
      });
      html += `</tbody></table>`;
      html += `<p class="hint">Ces heures ne varient pas avec l'effectif (elles dépendent des groupes déjà attribués) — seul le nombre de groupes nécessaires change ci-dessus.</p>`;
    }
    document.getElementById("simulation-result").innerHTML = html;
  } catch (err) { showToast(err.message, true); }
});

/* ===================== INITIALISATION ===================== */
document.addEventListener("DOMContentLoaded", async () => {
  initTabs();
  await loadFormations();
  await loadUEs();
  await loadEnseignants();
  await loadInterventions();
});
