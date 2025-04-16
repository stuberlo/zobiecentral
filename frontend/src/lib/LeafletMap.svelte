<script>
    // https://khromov.se/using-leaflet-with-sveltekit/
    import { onMount, onDestroy } from 'svelte';
    
    let { survivors } = $props();
    let mapElement;
    let map;
    let leaflet;

    onMount(async () => {
        leaflet = await import('leaflet');
        console.log('loading map', survivors)
        map = leaflet.map(mapElement).setView([55.712, 12.267], 12);

        leaflet.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // var myIcon = leaflet.icon({
        //   iconUrl: 'man-zombie.png',
        //   iconSize: [38, 38],
        // });
        // leaflet.marker([55.712, 12.267], {icon: myIcon}).addTo(map);
        // leaflet.marker([55.712, 12.268], {icon: myIcon}).addTo(map);
        // leaflet.marker([55.712, 12.269], {icon: myIcon}).addTo(map);
        // leaflet.marker([55.712, 12.369], {icon: myIcon}).addTo(map);
            
        for (const survivor of survivors.message) {
          console.log(survivor.icon)
          //let myIcon = leaflet.icon({
          //  iconUrl: "man-zombie.png",
          //  iconSize: [38, 38],
          //});
          leaflet.marker([survivor.last_location['lat'], survivor.last_location['lon']], {icon: leaflet.icon({
            iconUrl: survivor.icon,
            iconSize: [38, 38],
          })}).addTo(map)
          .bindPopup(
                  survivor.name + '<br>' + 
                  'ID: ' + survivor.id + '<br>' + 
                  'Gender: ' + survivor.gender + '<br>' + 
                  'Age: ' + survivor.age + '<br>' + 
                  'Inventory' + JSON.stringify(survivor.inventory) + '<br>' + 
                  'Infected flag count: ' + survivor.infected_flag_count + '<br>' + 
                  'Infected? ' + survivor.infected + '<br>' + 
                  'Last known location? ' + JSON.stringify(survivor.last_location)
          )
        }
        //for (survivor of survivors) {
        //  leaflet.marker([survivor.last_location['lat'], survivor.last_location['lon']], {icon: myIcon}).addTo(map);
        //}

        // leaflet.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        //     attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        // }).addTo(map);
     });

    onDestroy(async () => {
        if(map) {
            console.log('Unloading Leaflet map.');
            map.remove();
        }
    });

    //for (const survivor of survivors.message) {
    //  console.log(leaflet)
    //  //leaflet.marker([survivor.last_location['lat'], survivor.last_location['lon']], {icon: myIcon}).addTo(map);
    //}
</script>


<main>
    <div bind:this={mapElement}></div>
</main>

<style>
    @import 'leaflet/dist/leaflet.css';
    main div {
        height: 800px;
        z-index: 0;
    }
</style>
