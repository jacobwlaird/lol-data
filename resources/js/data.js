"use strict";
let roles = ['Top', 'Jungle', 'Middle', 'Support', 'ADC'];
let playerRoleLabels = document.querySelectorAll("td > label.playerRoleLabel");
let roleLabels = document.querySelectorAll(".roleLabel");
let getRole = document.querySelector("#getRoles");
let getChamps = document.querySelector("#getChamps");
let dragged;
//add the options to the select control, for all players
let roleSelectors = document.querySelectorAll(".roleSelect")

roleSelectors.forEach(function (select) {
    roles.forEach(function(role) {
        let roleOption = document.createElement("option");
        let roleText = document.createTextNode(role);
        roleOption.appendChild(roleText);
        select.appendChild(roleOption);
    });
});

getChamps.addEventListener('click',  function(evt){
    alert("Hey youre getting champs");
})

getRoles.addEventListener('click', function(evt){
    alert("Hey youre getting roles");
})

roleLabels.forEach(function (lbl) {
    lbl.addEventListener("dragstart", function(evt){
        role = evt.srcElement.innerHTML;
        dragged = evt.target;
    })
})

document.addEventListener("dragover", function( event ) {
    // prevent default to allow drop
    event.preventDefault();
}, false);

playerRoleLabels.forEach(function (lb) {
    lb.addEventListener("drop", function(ev) {
        dragged.parentNode.removeChild(dragged);
        ev.target.appendChild(dragged); 
        //append child
    });
});

//add event listener for the button to call to a python script