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

    // EVENTS - Should be overridden
    onExpand() {
    }

    onCollapse() {
    }

    // API
    setHeight(height) {
        this.style.height = `${height}px`
    }

    toggleExpansion() {
        if (!this.isExpanded) {  // expand
            this._isExpanded = true
            this.expansionToggle.style.rotate = "180deg"

            this.onExpand();
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
    static maxTracks = 5;

    collapsedHeight = 0;
    expandedHeight = 0;

    tracks = [];
    trackTemplate = this.querySelector(".spotify-track");

    nowPlaying = new Audio();
    nowPlayingIcon = null;

    constructor() {
        super();

        fetch("/api/spotify/songs/top")
            .then(r => {
                if (!r.ok) {
                    throw Error(r.statusText);
                }
                return r.json();
            }).then(data => this.updateSongs(data))
    }

    setTrack(elem, track) {
        let musicControl = elem.querySelector(".music-control");
        if (track["preview_url"] !== null) {
            musicControl.addEventListener("mouseup", (event) =>
                this.onPlayPause(event.currentTarget, track["preview_url"])
            )
            this._setIconPlaying(musicControl.children[0], false);
        } else {
            // Unable to play song so remove controls
            musicControl.remove();
        }

        elem.querySelector("figure div img").src = track["cover"];

        let title = elem.querySelector("div .title a");
        title.innerText = track["name"];
        title.href = track["url"];

        let artists = elem.querySelector("div .subtitle a");
        artists.innerText = "";
        for (let i = 0; i < track["artists"].length; i++) {
            let artist = document.createElement("a");
            artist.innerText = track["artists"][i]["name"];
            artist.href = track["artists"][i]["url"];

            artists.appendChild(artist);
            if (i !== track["artists"].length - 1) {
                artists.appendChild(document.createTextNode(", "));
            }
        }
    }

    updateSongs(data) {
        this.tracks = data["tracks"];

        if (this.tracks.length === 0) return;

        // Populate track elements
        this.setTrack(this.trackTemplate, this.tracks[0]);
        this.collapsedHeight = this.clientHeight;

        for (let i = 1; i < Math.min(this.tracks.length, SpotifyTile.maxTracks); i++) {
            let trackElem = this.trackTemplate.cloneNode(true);
            this.setTrack(trackElem, this.tracks[i]);
            this.trackTemplate.parentElement.appendChild(trackElem);
        }

        this.expandedHeight = this.clientHeight;
        this.onCollapse(0);
    }

    onExpand() {
        this.setHeight(this.expandedHeight);

        let trackElems = Array.from(this.querySelectorAll(".spotify-track"));
        for (let elem of trackElems.slice(1)) {
            elem.style.display = null;
        }
    }

    onCollapse(timeout = 500) {
        this.setHeight(this.collapsedHeight);

        setTimeout(() => {
            let trackElems = Array.from(this.querySelectorAll(".spotify-track"));
            for (let elem of trackElems.slice(1)) {
                elem.style.display = "none";
            }
        }, timeout)
    }

    _setIconPlaying(iconElem, playing) {
        if (playing === null) {  // null => spinning
            iconElem.classList.remove("fa-play");
            iconElem.classList.remove("fa-pause");
            iconElem.classList.add("spinning");
            iconElem.classList.add("fa-spinner");

        } else if (playing) {  // true => playing
            iconElem.classList.remove("spinning");
            iconElem.classList.remove("fa-spinner");
            iconElem.classList.remove("fa-play");
            iconElem.classList.add("fa-pause");

        } else {  // false => paused
            iconElem.classList.remove("spinning");
            iconElem.classList.remove("fa-spinner");
            iconElem.classList.remove("fa-pause");
            iconElem.classList.add("fa-play");
        }
    }

    onPlayPause(elem, url) {
        let iconElem = elem.querySelector("i");
        if (iconElem.classList.contains("spinning")) return;  // Still loading

        // Pause music
        if (iconElem.classList.contains("fa-pause")) {
            console.log("Pause music");
            this.nowPlaying.pause();
            this._setIconPlaying(iconElem, false);
            return;
        }

        // Resume previous song if possible
        if (this.nowPlaying.src === url) {
            this._setIconPlaying(iconElem, true);
            this.nowPlaying.play();
            return;
        }

        // Update icons
        if (this.nowPlayingIcon !== null) this._setIconPlaying(this.nowPlayingIcon, false);
        this._setIconPlaying(iconElem, null);
        this.nowPlayingIcon = iconElem;

        // Set new audio source
        this.nowPlaying.pause();
        this.nowPlaying = new Audio(url);
        this.nowPlaying.addEventListener("canplaythrough", () => {
            this._setIconPlaying(iconElem, true);
            this.nowPlaying.play();
        })
        this.nowPlaying.addEventListener("ended", () => {
            this._setIconPlaying(iconElem, false);
        })
    }
}


// Register all tiles
[
    AboutMeTile,
    SpotifyTile
].map(registerTile)
