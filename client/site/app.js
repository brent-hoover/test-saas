// Browser client: logs in through Keycloak's authorization-code flow (PKCE),
// then shows the username and groups returned by GET /api/groups.
// Globals: window.TEST_SAAS_CONFIG (config.js) and window.oidc (vendored library).

const config = window.TEST_SAAS_CONFIG;

const userManager = new window.oidc.UserManager({
  authority: config.issuerUrl,
  client_id: config.clientId,
  redirect_uri: config.redirectUri,
  response_type: "code",
  scope: "openid profile",
});

const statusLine = document.getElementById("status");

async function main() {
  if (isReturnFromKeycloak()) {
    // Exchanges the authorization code for tokens (PKCE verifier from session storage).
    await userManager.signinRedirectCallback();
    window.history.replaceState({}, "", window.location.pathname);
  }

  const user = await userManager.getUser();
  if (user === null || user.expired) {
    statusLine.textContent = "Redirecting to Keycloak…";
    await userManager.signinRedirect();
    return;
  }

  statusLine.textContent = "Logged in.";
  await showGroups(user.access_token);
}

function isReturnFromKeycloak() {
  const params = new URLSearchParams(window.location.search);
  return params.has("code") || params.has("error");
}

async function showGroups(accessToken) {
  const response = await fetch("/api/groups", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!response.ok) {
    throw new Error(`GET /api/groups returned ${response.status}`);
  }
  const authenticatedUser = await response.json();
  renderAuthenticatedUser(authenticatedUser);
}

function renderAuthenticatedUser({ username, groups }) {
  // textContent only: claim values come from the token and are never parsed as HTML.
  document.getElementById("username").textContent = username;
  const groupList = document.getElementById("groups");
  groupList.replaceChildren(
    ...groups.map((group) => {
      const item = document.createElement("li");
      item.textContent = group;
      return item;
    }),
  );
  document.getElementById("no-groups").hidden = groups.length > 0;
  document.getElementById("identity").hidden = false;
}

main().catch((error) => {
  statusLine.textContent = `Error: ${error.message}`;
  statusLine.classList.add("error");
});
