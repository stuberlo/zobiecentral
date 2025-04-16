
<script>
  import {onMount} from 'svelte';
  import { Button, Modal, Label, Input, Checkbox, Alert, Li, List } from 'flowbite-svelte';
  import { InfoCircleSolid } from 'flowbite-svelte-icons';
  import LeafletMap from '$lib/LeafletMap.svelte';
  let formRegister = false;
  let formUpdateLocation = false;
  let formFlagInfected = false;
  let formViewSurvivor = false;
  let formTradeItems = false;
  export let trader1;
  export let trader2;
  export let form;
  export let data;
  console.log(form)
  console.log(trader1)
  console.log(trader2)
      //for (const [key, value] of Object.entries(object1)) {
      //  console.log(`${key}: ${value}`);

  const getSurvivor = async function(e) {
    //console.log('getSurvivor', e.target.value, e.target.id)
    const response = await fetch('/api/survivors/' + e.target.value)
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }
    const result = await response.json();
    if (e.target.id == "trader1") {
      trader1 = result
    } else if (e.target.id == "trader2") {
      trader2 = result
    }
  }



</script>

{#if form?.error}

<Alert class="items-start!" dismissable>
  <span slot="icon">
    <InfoCircleSolid class="w-5 h-5" />
    <span class="sr-only">Info</span>
  </span>
  <p class="font-medium">{form.message[0]}</p>
  <ul class="mt-1.5 ms-4 list-disc list-inside">
    {#each form.message.slice(1) as message}
       <Li class="space-y-1"> {message} </Li>
    {/each}
  </ul>
</Alert>

{:else if form?.success}

<Alert color="green" dismissable>
  <p class="font-medium">Success</p>
    {#if form?.message}
      {#each Object.entries(form.message) as [key, value]}
          <Li class="space-y-1"> {key} : {JSON.stringify(value)} </Li>
      {/each}
    {/if}
  <ul class="mt-1.5 ms-4 list-disc list-inside">
  </ul>
</Alert>

{/if}

<h1 class="fancy_big_header">Zombie Survival Center</h1>

<hr>
<div class="banner divide-x-3 divide-solid divide-red-100">
    <div class="action_button" on:click={() => (formRegister = true)}> Register Survivor</div>
    <div class="action_button" on:click={() => (formUpdateLocation = true)}> Update Survivor Location</div>
    <div class="action_button" on:click={() => (formFlagInfected = true)}> Flag Survivor as infected </div>
    <div class="action_button" on:click={() => (formViewSurvivor = true)}> View Survivor Data </div>
    <div class="action_button" on:click={() => (formTradeItems = true)}> Trade Items </div>
</div>
<hr>


<!-- https://flowbite-svelte.com/docs/components/modal -->

<!-- https://vercel.com/guides/using-sveltekit-form-actions -->


<Modal bind:open={formRegister} size="xs" autoclose={false} class="w-full modal ontop">
  <form class="flex flex-col space-y-6" action="?/register" method="POST">
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">Register a new survivor</h3>
    <Label class="space-y-1">
      <span>Name*</span>
      <Input name="name" placeholder="" required />
    </Label>
    <Label class="space-y-1">
      <span>Age* </span>
      <Input type="number" name="age" placeholder="" required />
    </Label>
    <Label class="space-y-1">
      <span>Gender* </span>
      <Input name="gender" placeholder="" required />
    </Label>
    <Label class="space-y-1">
      <span>Last location* </span>
      <div class="grid grid-cols-2 divide-x-3 divide-solid divide-red-100">
      <Input name="lat" placeholder="Latitude" required />
      <Input name="lon" placeholder="Longitude" required />
      </div>
    </Label>
    <Label class="space-y-1">
      <span>Inventory </span>
      <div>
        <Input type="number" name="water" placeholder="Water"/>
        <Input type="number" name="food" placeholder="Food"/>
        <Input type="number" name="medication" placeholder="Medication"/>
        <Input type="number" name="ammunition" placeholder="Ammunition"/>
        <Input name="other" placeholder="Other: item_1=3,item_2=1..."/>
      </div>
    </Label>
    <Button type="submit" class="w-full1">Register</Button>
  </form>
  </Modal>

<Modal bind:open={formUpdateLocation} size="xs" autoclose={false} class="w-full modal">
  <form class="flex flex-col space-y-6" action="?/update_location" method="POST">
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">Update survivor location</h3>
    <Label class="space-y-1">
      <span>ID*</span>
      <Input type="number" name="id" placeholder="" required />
    </Label>
    <Label class="space-y-1">
      <span>Last location* </span>
      <div class="grid grid-cols-2 divide-x-3 divide-solid divide-red-100">
      <Input type="number" name="lat" placeholder="Latitude" required />
      <Input type="number" name="lon" placeholder="Longitude" required />
      </div>
    </Label>
    <Button type="submit" class="w-full1">Update</Button>
  </form>
</Modal>

<Modal bind:open={formFlagInfected} size="xs" autoclose={false} class="w-full modal">
  <form class="flex flex-col space-y-6" action="?/flag_as_infected" method="POST">
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">Flag survivor as infected</h3>
    <Label class="space-y-1">
      <span>ID*</span>
      <Input type="number" name="id" placeholder="" required />
    </Label>
    <Button type="submit" class="w-full1">Flag</Button>
  </form>
</Modal>

<Modal bind:open={formViewSurvivor} size="xs" autoclose={false} class="w-full modal">
  <form class="flex flex-col space-y-6" action="?/view_surivor" method="POST">
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">View Survivor</h3>
    <Label class="space-y-1">
      <span>ID*</span>
      <Input type="number" name="id" placeholder="" required />
    </Label>
    <Button type="submit" class="w-full1">View</Button>
  </form>
</Modal>

<Modal bind:open={formTradeItems} size="xs" autoclose={false} class="w-full modal">
  <form class="flex flex-col space-y-6" action="?/trade_items" method="POST">
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">Trade items</h3>
    <div class="grid grid-cols-2">
      <div class="m-4">
        <Label class="space-y-1">
          <span>ID*</span>
          <Input id="trader1" on:change={getSurvivor} type="number" name="s1_id" placeholder="" required />
        </Label>
        <Label class="space-y-1">
          {#if trader1}
            <p> <b>Name: </b> {trader1.name} </p>
            <p> <b>Infected: </b> {trader1.infected} </p>
            <span><b>Inventory: </b></span>

            {#each Object.entries(trader1.inventory) as [item, amount]}
                {#if amount}
                  <Li class="space-y-1"> {item} </Li>
                  <Input type="number" name={item + "_1"} value={amount}/>
                {/if}
            {/each}

          {/if}
        </Label>
      </div>
      <div class="m-4">
        <Label class="space-y-1">
          <span>ID*</span>
          <Input id="trader2" on:change={getSurvivor} type="number" name="s2_id" placeholder="" required />
        </Label>
        <Label class="space-y-1">
          {#if trader2}
            <p> <b>Name: </b> {trader2.name} </p>
            <p> <b>Infected: </b> {trader2.infected} </p>
            <span><b>Inventory: </b></span>

            {#each Object.entries(trader2.inventory) as [item, amount]}
                {#if amount}
                  <Li class="space-y-1"> {item} </Li>
                  <Input type="number" name={item + "_2"} value={amount}/>
                {/if}
            {/each}

          {/if}
        </Label>
      </div>
    </div>
    <Button type="submit" class="w-full1" disabled={!(trader1?.name && trader2?.name && !trader1?.infected && !trader2?.infected && trader1.id!=trader2.id)}>{trader1?.infected || trader2?.infected ? "Don't trade with infected survivors!" : trader1?.id == trader2?.id ? "Choose two different survivors" : "Trade"}</Button>
  </form>
</Modal>

<LeafletMap survivors={data}/>


<style>
  .fancy_big_header {
    font-family: "Courier New", monospace;
    font-size: 40px;
    color: orange;
    font-weight: bold;
    display: inline;
    text-align: center;
  }
  .banner {
    display: grid;
    grid-template-columns: auto auto auto auto auto;
  }
  .action_button {
    display: grid;
    font-family: "Courier New", monospace;
    font-size: 12px;
    font-weight: bold;
    text-align: center;
    color: red;
    margin: 4px;
    padding: 4px;
    height: 30px;
  }
  .action_button:hover {
    background: repeating-linear-gradient(
      45deg,
      #fff9c4,
      #fff9c4 10px,
      #a3a3a3 10px,
      #a3a3a3 20px
    );
  }
</style>
