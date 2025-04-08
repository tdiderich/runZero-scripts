# 🛠️ Pull Request Template

Please choose the relevant section below based on the type of change you're making.

---

## 🔁 Integration Update

_Use this section if you're updating an existing integration._

### Description

Please describe the changes made to the existing integration and why they were necessary. Include any relevant context, such as bug fixes, feature updates, or improvements to configuration.

### Checklist

- [ ] **Validated in Customer Environment:** Changes have been tested in a customer environment and verified to work as expected.  
- [ ] **Updated README:** The README has been updated to reflect any changes to configuration, setup, or usage.

---

## 🆕 New Integration

_Use this section if you're submitting a new integration._

### Description

Please provide a brief description of your changes and the context for this integration. Include any background details or links to related issues.

### Checklist

- [ ] **Add label:** Add the `new-integration` label to this PR for the correct automation to trigger on this PR.
- [ ] **New Integration Folder:** A new folder has been created for the integration.  
- [ ] **Updated README:** The README has been updated based on the boilerplate to reflect the new integration details.  
- [ ] **customer-integration.star File:** The `customer-integration-<name>.star` file has been created/updated as required.  
- [ ] **config.json File:** The `config.json` is updated with the `name` (product name) and `type` (inbound or outbound) of integration.

---

> 📝 _Feel free to delete the section that doesn't apply._
