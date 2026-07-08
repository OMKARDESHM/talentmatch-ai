import { Component } from "react";

const DEFAULT_ERROR_MESSAGE =
  "TalentMatch encountered an unexpected interface error. "
  + "Reload the application to restore your workspace.";

export default class AppErrorBoundary extends Component {
  constructor(props) {
    super(props);

    this.state = {
      hasError: false,
    };
  }

  static getDerivedStateFromError() {
    return {
      hasError: true,
    };
  }

  componentDidCatch(error, errorInfo) {
    console.error(
      "TalentMatch UI error",
      error,
      errorInfo,
    );
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <main className="app-error-screen">
          <section className="app-error-card">
            <div className="brand-mark" aria-hidden="true">
              TM
            </div>

            <div>
              <p className="eyebrow">APPLICATION RECOVERY</p>
              <h1>Something went wrong</h1>
              <p className="app-error-description">
                {DEFAULT_ERROR_MESSAGE}
              </p>
            </div>

            <button
              className="primary-button"
              type="button"
              onClick={this.handleReload}
            >
              Reload application
            </button>
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}
