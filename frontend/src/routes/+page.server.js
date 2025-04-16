import { fail } from '@sveltejs/kit';
import {
  getRegisterSurvivorData,
  getUpdateLocationData,
  getTradeData,
  getId,
} from './actions.js'

/** @type {import('./$types').PageServerLoad} */
export async function load({ fetch }) {
  const response = await fetch('/api/survivors/')
  if (!response.ok) {
      return await formatError(response)
  }
  const result = await response.json();
  return { success: true, message: result };
}

async function formatError(response) {
  const result = await response.json();
  console.log(result)
  if (typeof(result.detail) == "object") {
    return fail(response.status, {error: true, message: ["Error:"].concat(result.detail.map(JSON.stringify))})
  }
  const detail = result.detail.split('\n')
  let errorMessage = [detail[0]]
  for (let i = 1; i < detail.length; i+=3) {
    errorMessage.push(detail[i] + ': ' + detail[i+1])
  }
  return fail(response.status, {error: true, message: errorMessage})
}

async function apiCall(request, fetch, endpoint, getBody, method) {
    const data = await request.formData();
    const [queryParams, body] = getBody(data) 
    console.log(queryParams, body)
    const response = await fetch(endpoint + queryParams, Object.assign({}, {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
    }, method == "POST" ? { body: JSON.stringify(body)} : {})
    )
    if (!response.ok) {
        return await formatError(response)
    }
    const result = await response.json();
    return { success: true, message: result };
}


/** @satisfies {import('./$types').Actions} */
export const actions = {
	register: async ({request, fetch}) => {
    return apiCall(request, fetch, '/api/survivors/', getRegisterSurvivorData, "POST")
  },
	update_location: async ({request, fetch}) => {
    return apiCall(request, fetch, '/api/update_location/', getUpdateLocationData, "POST")
  },
	flag_as_infected: async ({request, fetch}) => {
    return apiCall(request, fetch, '/api/flag_as_infected/', getId, "GET")
  },
	view_surivor: async ({request, fetch}) => {
    return apiCall(request, fetch, '/api/survivors/', getId, "GET")

  },
	trade_items: async ({request, fetch}) => {
    return apiCall(request, fetch, '/api/trade_items/', getTradeData, "POST")
  }
}

