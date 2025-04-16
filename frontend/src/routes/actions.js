export function getRegisterSurvivorData(data) {
    let inventory = {}
    for (const item of ['water', 'food', 'medication', 'ammunition']) {
      const amount = data.get(item)
      if (amount) {
        inventory[item] = amount
      }
    }
    const other = data.get('other')
    if (other) {
      for (let item of other.split(',')) {
        let [itm, amount] = item.split('=')
        inventory[itm] = amount
      }
    }
    return ['', {
        name: data.get('name'),
        gender: data.get('gender'),
        age: data.get('age'),
        last_location: {
          "lat": data.get('lat'),
          "lon": data.get('lon')
        },
        inventory: inventory
    }]
}

export function getUpdateLocationData(data) {
    return [data.get('id'), {
      "lat": data.get('lat'),
      "lon": data.get('lon')
    }]
}

export function getId(data) {
    return [data.get('id'), {}]
}

export function getTradeData(data) {
    console.log(data)
    let s1_id = 0
    let s2_id = 0
    let s1_trades = {}
    let s2_trades = {}
    
    for (const [item, amount] of data) {
      if (item.slice(-2) == '_1' && amount > 0) {
        s1_trades[item.slice(0, -2)] = amount
      } else if (item.slice(-2) == '_2' && amount > 0) {
        s2_trades[item.slice(0, -2)] = amount
      } else if (item.slice(0,2) == 's1') {
        s1_id = amount
      } else if (item.slice(0,2) == 's2') {
        s2_id = amount
      }
    }
    return ['', {
        s1_id,
        s2_id,
        s1_trades,
        s2_trades,
    }]
}
