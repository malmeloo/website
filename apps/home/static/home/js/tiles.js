"use strict";

class RootTile extends HTMLElement {
    static tileId = "root-tile";
    _expansion_toggle;

    constructor() {
        super();

        // Construct element from template
        const template = document.getElementById(this.localName);
        if (template == null) return;  // elem not used on webpage
        this.appendChild(template.content.cloneNode(true));

        // Register element that toggles expansion
        this._expansion_toggle = this.querySelector(".toggle-expand");
        if (this.expansionToggle) {
            this.expansionToggle.addEventListener("click", _ => this.toggleExpansion());
        }

        this.fillSlots();
    }

    static get observedAttributes() {
        return ['height', 'c', 'l'];
    }

    _isExpanded = false;

    // GETTERS
    get isExpanded() {
        return this._isExpanded
    }

    get expansionToggle() {
        return this._expansion_toggle
    }

    fillSlots() {
        let slots = this.querySelectorAll("slot");

        let fillers = {}
        for (let filler of this.querySelectorAll("[slot]")) {
            fillers[filler.slot] = (fillers[filler.slot] ?? []).concat([filler]);
            filler.remove();  // detach so we can treat is as a "virtual" node
        }

        // Actually replace the slot nodes with their fillers
        for (let slot of slots) {
            let target = fillers[slot.name];
            if (target) slot.replaceWith(...target);
        }
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log(name, oldValue, newValue);
    }

    // EVENTS - Should be overridden
    onExpansion() {
    }

    onCollapse() {
    }

    // API
    setHeight(height) {
        let heightPx = height * this.offsetWidth;
        this.style.height = `${heightPx}px`
    }

    toggleExpansion() {
        if (!this.isExpanded) {  // expand
            this._isExpanded = true
            this.expansionToggle.style.rotate = "180deg"

            this.onExpansion();
        } else {  // collapse
            this._isExpanded = false;
            this.expansionToggle.style.rotate = "0deg"

            this.onCollapse();
        }
    }
}

function registerTile(tile) {
    if (tile.tileId === undefined) throw new Error("Couldn't find tile id (must subclass RootTile!)");
    if (tile.tileId === "root-tile") throw new Error("Cannot register root tile (must override id field!)");

    customElements.define(tile.tileId, tile);
}


// Tile definition
class AboutMeTile extends RootTile {
    static tileId = "about-me-tile";
}

class SpotifyTile extends RootTile {
    static tileId = "spotify-tile";
}


// Register all tiles
[
    AboutMeTile,
    SpotifyTile
].map(registerTile)
