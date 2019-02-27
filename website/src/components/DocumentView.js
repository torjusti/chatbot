import React from "react";
import { fetchData } from "../utils/Util";

export default class DocumentView extends React.Component {
  constructor() {
    super();
    this.state = {
      inputValue: "hardcoded text"
    }
  }

  async componentDidMount() {
    // Fetch content
    const data = { "data": { "id": this.props.id } };
    const content = await fetchData("http://localhost:8080/v1/get_content", data);
    if (! "manual" in content) {
      this.setState({ manual: content.prod, automatic: content.prod });
    } else {
      this.setState({ manual: content.manual, automatic: content.prod });
    }
  }

  handleSubmit = async (e) => {
    e.preventDefault();
    // Save data and delete entry in manual collection if needed
    const data = { "data": { "id": this.props.id, "content": this.state.manual } };
    const content = await fetchData("http://localhost:8080/v1/update_content", data);
    this.props.changeView("main");
  }

  createNewKeyword = (e) => {
    e.preventDefault();
    if (this.state.manual) {
      this.setState(prevState => ({
        manual: {
          ...prevState.manual,
          keywords: [
            ...prevState.manual.keywords,
            { "keyword": "", "confidence": 1 },
          ],
        },
      }));
    }
  }

  deleteKeyword = (e, i) => {
    e.preventDefault();
    this.setState(prevState => ({
      manual: {
        ...prevState.manual,
        keywords: [
          ...prevState.manual.keywords.slice(0, i),
          ...prevState.manual.keywords.slice(i + 1),
        ],
      },
    }));
  }

  render() {
    let textAreasManual;
    if (this.state.manual) {
      textAreasManual = this.state.manual.texts.map((text, i) => (
        <textarea
          key={i}
          rows="10"
          value={text}
          onChange={(e) => {
            const value = e.target.value;

            this.setState(prevState => ({
              manual: {
                ...prevState.manual,
                texts: [
                  ...prevState.manual.texts.slice(0, i),
                  value,
                  ...prevState.manual.texts.slice(i + 1),
                ],
              },
            }));
          }
          } />
      ));
    }

    let keywordsManual;
    if (this.state.manual) {
      keywordsManual = this.state.manual.keywords.map((keyword, i) => (
        <div key={i} className="keyword">
          <input
            type="text"
            value={keyword["keyword"]}
            onChange={(e) => {
              const value = e.target.value;
              this.setState(prevState => ({
                manual: {
                  ...prevState.manual,
                  keywords: [
                    ...prevState.manual.keywords.slice(0, i),
                    { "keyword": value, "confidence": prevState.manual.keywords[i].confidence },
                    ...prevState.manual.keywords.slice(i + 1),
                  ],
                },
              }));
            }
            }
          ></input>
          <input
            type="number"
            min="0"
            max="1"
            step="0.000000000000000001"
            value={keyword["confidence"]}
            onChange={(e) => {
              const value = parseFloat(e.target.value);
              this.setState(prevState => ({
                manual: {
                  ...prevState.manual,
                  keywords: [
                    ...prevState.manual.keywords.slice(0, i),
                    { "keyword": prevState.manual.keywords[i].keyword, "confidence": value },
                    ...prevState.manual.keywords.slice(i + 1),
                  ],
                },
              }));
            }
            }
          ></input>
          <button
            onClick={(e) => this.deleteKeyword(e, i)}
          >Slett nøkkelord</button>
        </div>
      ));
    }

    let textAreasAutomatic;
    if (this.state.automatic) {
      textAreasAutomatic = this.state.automatic.texts.map((text, i) => (
        <textarea
          readOnly
          key={i}
          rows="10"
          value={text}
        />
      ));
    }

    let keywordsAutomatic;
    if (this.state.automatic) {
      keywordsAutomatic = this.state.automatic.keywords.map((keyword, i) => (
        <div key={i} className="keyword">
          <input
            readOnly
            type="text"
            value={keyword["keyword"]}
          ></input>
          <input
            readOnly
            type="text"
            value={keyword["confidence"]}
          ></input>
        </div>
      ));
    }

    return (
      <div>
        <h1>Content</h1>
        {this.state.manual &&
          <div>
            <h2>Manual</h2>
            <form onSubmit={(e) => this.handleSubmit(e)}>
              {textAreasManual}
              {keywordsManual}
              <button onClick={(e) => this.createNewKeyword(e)}>Nytt nøkkelord</button>
              <input type="submit" value="Save" />
            </form>
          </div>
        }
        {this.state.automatic &&
          <div>
            <h2>Automatic</h2>
            {textAreasAutomatic}
            {keywordsAutomatic}
          </div>
        }
      </div >
    );
  }
}