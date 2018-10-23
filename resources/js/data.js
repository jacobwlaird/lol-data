"use strict";

let playerRoleLabels = document.querySelectorAll(".playerRoleLabel");
let roleLabels = document.querySelectorAll(".roleLabel");
let role = "";
let dragged;

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